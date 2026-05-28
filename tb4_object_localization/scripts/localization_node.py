#!/usr/bin/env python3

import math

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import CameraInfo, Image
from visualization_msgs.msg import Marker

from cv_bridge import CvBridge

import tf2_ros
import tf2_geometry_msgs

# Expected detection message from module 2.
# This may need to be changed after the vision member confirms the interface.
from vision_msgs.msg import Detection2DArray


class LocalizationNode(Node):
    """ROS 2 node for 3D object localization from 2D detection + depth."""

    def __init__(self):
        super().__init__("object_localization")

        # Declare parameters from localization.yaml
        self.declare_parameter("detection_topic", "/detected_objects_2d")
        self.declare_parameter("depth_topic", "/depth/image")
        self.declare_parameter("camera_info_topic", "/camera_info")

        self.declare_parameter("target_pose_camera_topic", "/target_object_pose_camera")
        self.declare_parameter("target_pose_map_topic", "/target_object_pose_map")
        self.declare_parameter("marker_topic", "/object_marker")

        self.declare_parameter("camera_frame", "camera_depth_optical_frame")
        self.declare_parameter("target_frame", "map")

        self.declare_parameter("min_depth", 0.2)
        self.declare_parameter("max_depth", 5.0)
        self.declare_parameter("confidence_threshold", 0.5)
        self.declare_parameter("target_class", "")

        # Read parameters
        self.detection_topic = self.get_parameter("detection_topic").value
        self.depth_topic = self.get_parameter("depth_topic").value
        self.camera_info_topic = self.get_parameter("camera_info_topic").value

        self.target_pose_camera_topic = self.get_parameter("target_pose_camera_topic").value
        self.target_pose_map_topic = self.get_parameter("target_pose_map_topic").value
        self.marker_topic = self.get_parameter("marker_topic").value

        self.camera_frame = self.get_parameter("camera_frame").value
        self.target_frame = self.get_parameter("target_frame").value

        self.min_depth = float(self.get_parameter("min_depth").value)
        self.max_depth = float(self.get_parameter("max_depth").value)
        self.confidence_threshold = float(self.get_parameter("confidence_threshold").value)
        self.target_class = self.get_parameter("target_class").value

        # Camera intrinsics
        self.fx = None
        self.fy = None
        self.cx = None
        self.cy = None

        # Latest depth image
        self.latest_depth_image = None
        self.latest_depth_header = None

        self.bridge = CvBridge()

        # TF listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Publishers
        self.pose_camera_pub = self.create_publisher(
            PoseStamped,
            self.target_pose_camera_topic,
            10,
        )
        self.pose_map_pub = self.create_publisher(
            PoseStamped,
            self.target_pose_map_topic,
            10,
        )
        self.marker_pub = self.create_publisher(
            Marker,
            self.marker_topic,
            10,
        )

        # Subscribers
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            self.camera_info_topic,
            self.camera_info_callback,
            10,
        )
        self.depth_sub = self.create_subscription(
            Image,
            self.depth_topic,
            self.depth_callback,
            10,
        )
        self.detection_sub = self.create_subscription(
            Detection2DArray,
            self.detection_topic,
            self.detection_callback,
            10,
        )

        self.get_logger().info("TB4 object localization node started")
        self.get_logger().info(f"Detection topic: {self.detection_topic}")
        self.get_logger().info(f"Depth topic: {self.depth_topic}")
        self.get_logger().info(f"Camera info topic: {self.camera_info_topic}")
        self.get_logger().info(f"Target frame: {self.target_frame}")

    def camera_info_callback(self, msg: CameraInfo):
        """Store camera intrinsic parameters."""
        self.fx = msg.k[0]
        self.fy = msg.k[4]
        self.cx = msg.k[2]
        self.cy = msg.k[5]

    def depth_callback(self, msg: Image):
        """Store latest depth image."""
        try:
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            self.latest_depth_image = depth_image
            self.latest_depth_header = msg.header
        except Exception as exc:
            self.get_logger().warn(f"Failed to convert depth image: {exc}")

    def detection_callback(self, msg: Detection2DArray):
        """Convert 2D detections to 3D pose using depth and camera info."""
        if self.latest_depth_image is None:
            self.get_logger().warn("No depth image received yet")
            return

        if self.fx is None or self.fy is None or self.cx is None or self.cy is None:
            self.get_logger().warn("No camera info received yet")
            return

        if not msg.detections:
            return

        for detection in msg.detections:
            # vision_msgs/Detection2D uses bbox center + size in pixels
            u = int(detection.bbox.center.position.x)
            v = int(detection.bbox.center.position.y)

            pose_camera = self.pixel_to_camera_pose(u, v, msg.header.stamp)
            if pose_camera is None:
                continue

            self.pose_camera_pub.publish(pose_camera)

            pose_map = self.transform_pose_to_target_frame(pose_camera)
            if pose_map is not None:
                self.pose_map_pub.publish(pose_map)
                self.publish_marker(pose_map)

            # Process only the first valid detection for now
            break

    def pixel_to_camera_pose(self, u: int, v: int, stamp) -> PoseStamped | None:
        """Project image pixel and depth value to 3D camera coordinates."""
        height, width = self.latest_depth_image.shape[:2]

        if u < 0 or u >= width or v < 0 or v >= height:
            self.get_logger().warn(f"Detection center out of image bounds: u={u}, v={v}")
            return None

        depth = float(self.latest_depth_image[v, u])

        # Many depth images are uint16 in millimeters. Convert to meters if needed.
        if self.latest_depth_image.dtype.name == "uint16":
            depth = depth / 1000.0

        if math.isnan(depth) or math.isinf(depth):
            self.get_logger().warn("Invalid depth value")
            return None

        if depth < self.min_depth or depth > self.max_depth:
            self.get_logger().warn(f"Depth out of range: {depth:.2f} m")
            return None

        x = (u - self.cx) * depth / self.fx
        y = (v - self.cy) * depth / self.fy
        z = depth

        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = self.camera_frame

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

        pose.pose.orientation.w = 1.0

        return pose

    def transform_pose_to_target_frame(self, pose_camera: PoseStamped) -> PoseStamped | None:
        """Transform object pose from camera frame to target frame, normally map."""
        try:
            pose_target = self.tf_buffer.transform(
                pose_camera,
                self.target_frame,
                timeout=Duration(seconds=0.5),
            )
            return pose_target
        except Exception as exc:
            self.get_logger().warn(
                f"Failed to transform pose from {pose_camera.header.frame_id} "
                f"to {self.target_frame}: {exc}"
            )
            return None

    def publish_marker(self, pose: PoseStamped):
        """Publish RViz marker for localized object."""
        marker = Marker()
        marker.header = pose.header
        marker.ns = "localized_objects"
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        marker.pose = pose.pose

        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2

        marker.color.r = 1.0
        marker.color.g = 0.2
        marker.color.b = 0.2
        marker.color.a = 0.8

        self.marker_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = LocalizationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()