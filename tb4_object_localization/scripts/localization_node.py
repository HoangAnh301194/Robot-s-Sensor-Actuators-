#!/usr/bin/env python3
import numpy as np
import rclpy
import tf2_ros
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped, PoseStamped
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import CameraInfo, Image
from visualization_msgs.msg import Marker
from vision_msgs.msg import Detection2DArray

class ObjectLocalizationNode(Node):
    def __init__(self):
        super().__init__("object_localization_node")
        self.bridge = CvBridge()

        # Biến lưu thông số camera (Intrinsics)
        self.fx = self.fy = self.cx = self.cy = None

        # TF Broadcaster để phát tọa độ lên RViz
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Publisher gửi vị trí vật thể cho Mission Manager
        self.pose_pub = self.create_publisher(PoseStamped, self.target_pose_topic, 10)
        self.marker_pub = self.create_publisher(Marker, self.marker_topic, 10)

        # Đăng ký nhận thông số Camera
        self.create_subscription(
            CameraInfo, self.camera_info_topic, self.camera_info_callback, 10
        )
        # Đăng ký nhận ảnh Chiều sâu (Depth)
        self.create_subscription(
            Image, self.depth_topic, self.depth_callback, 10
        )
        # Đăng ký nhận kết quả nhận diện 2D từ module Vision
        self.create_subscription(
            Detection2DArray, self.detections_topic, self.detection_callback, 10
        )

        # Biến lưu tọa độ (u, v) trung tâm vật thể phát hiện được
        self.detected_u = None
        self.detected_v = None
        self.detected_size_x = 0.0
        self.detected_size_y = 0.0
        self.detected_class_id = None
        self.detected_score = 0.0

        self.get_logger().info("Node 3D Object Localization đã khởi động!")

    def camera_info_callback(self, msg):
        if self.fx is None:
            self.fx = msg.k[0]
            self.cx = msg.k[2]
            self.fy = msg.k[4]
            self.cy = msg.k[5]

    def detection_callback(self, msg):
        # Khi nhận được vật thể mới, cập nhật tọa độ u, v
        if len(msg.detections) > 0:
            det = self.select_person_detection(msg.detections)
            self.detected_u = int(det.bbox.center.position.x)
            self.detected_v = int(det.bbox.center.position.y)
            self.detected_size_x = float(det.bbox.size_x)
            self.detected_size_y = float(det.bbox.size_y)
            self.detected_class_id = det.results[0].hypothesis.class_id if det.results else ""
            self.detected_score = det.results[0].hypothesis.score if det.results else 0.0
            # self.get_logger().info(f"Đã nhận diện vật thể tại: ({self.detected_u}, {self.detected_v})")
        else:
            self.detected_u = None
            self.detected_v = None
            self.detected_size_x = 0.0
            self.detected_size_y = 0.0
            self.detected_class_id = None
            self.detected_score = 0.0

    def select_person_detection(self, detections):
        # YOLOv8 COCO: class_id "0" là person. Nếu không có person thì lấy detection đầu tiên.
        person_detections = [
            det for det in detections
            if det.results and det.results[0].hypothesis.class_id == "0"
        ]
        candidates = person_detections if person_detections else detections
        return max(
            candidates,
            key=lambda det: det.results[0].hypothesis.score if det.results else 0.0,
        )

    def depth_callback(self, msg):
        if self.fx is None:
            return
        
        # Chỉ tính toán nếu có tọa độ vật thể từ module Vision
        if self.detected_u is not None and self.detected_v is not None:
            try:
                depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
                height, width = depth_image.shape

                # Giới hạn tọa độ trong phạm vi ảnh
                u = min(self.detected_u, width - 1)
                v = min(self.detected_v, height - 1)

                # Lấy khoảng cách Z bằng median quanh tâm bbox để tránh pixel depth lỗi.
                Z_m = self.get_depth_meters(depth_image, u, v)
                if Z_m is None:
                    return

                # Tính tọa độ 3D (Xc, Yc, Zc) theo mô hình Pinhole
                X_c = (u - self.cx) * Z_m / self.fx
                Y_c = (v - self.cy) * Z_m / self.fy
                Z_c = Z_m

                # 1. Publish TF (cho RViz2)
                frame_id = self.resolve_camera_frame(msg.header.frame_id)
                self.publish_tf(X_c, Y_c, Z_c, msg.header.stamp, frame_id)

                # 2. Publish Pose (cho Mission Manager)
                # Chuyển đổi từ tọa độ camera (Xc, Yc, Zc) sang tọa độ map theo chuẩn ROS
                pose_msg = PoseStamped()
                pose_msg.header = msg.header
                pose_msg.header.frame_id = frame_id
                
                # Ánh xạ trục: X_cam -> Z_ros (sâu), Y_cam -> -X_ros (ngang), Z_cam -> -Y_ros (cao)
                # Lưu ý: Tọa độ này vẫn đang trong hệ quy chiếu của camera (oakd_link).
                # Để mission manager đi tới được, ta cần đổi sang hệ map (cần TF lookup), 
                # nhưng trong mô phỏng đơn giản, ta sẽ gửi tọa độ tương đối so với robot.
                pose_msg.pose.position.x = Z_c   # Tiến/Lùi
                pose_msg.pose.position.y = -X_c  # Trái/Phải
                pose_msg.pose.position.z = -Y_c  # Cao/Thấp
                pose_msg.pose.orientation.w = 1.0

                self.pose_pub.publish(pose_msg)
                self.publish_marker(pose_msg)

            except Exception as e:
                self.get_logger().error(f"Lỗi tính toán Depth: {e}")

    def publish_marker(self, pose_msg):
        marker = Marker()
        marker.header = pose_msg.header
        marker.ns = "target_object"
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose = pose_msg.pose
        marker.scale.x = 0.35
        marker.scale.y = 0.35
        marker.scale.z = 0.35
        marker.color.r = 1.0
        marker.color.g = 0.15
        marker.color.b = 0.0
        marker.color.a = 1.0
        marker.lifetime = Duration(seconds=0.8).to_msg()
        self.marker_pub.publish(marker)

    def get_depth_meters(self, depth_image, u, v):
        height, width = depth_image.shape
        half_window = max(
            2,
            min(12, int(min(self.detected_size_x, self.detected_size_y) * 0.08)),
        )
        u_min = max(0, u - half_window)
        u_max = min(width, u + half_window + 1)
        v_min = max(0, v - half_window)
        v_max = min(height, v + half_window + 1)

        depth_patch = np.asarray(depth_image[v_min:v_max, u_min:u_max], dtype=np.float32)
        valid_depths = depth_patch[np.isfinite(depth_patch) & (depth_patch > 0.0)]
        if valid_depths.size == 0:
            return None

        depth_value = float(np.median(valid_depths))
        if depth_value > 20.0:
            depth_value /= 1000.0

        if depth_value <= 0.02 or depth_value > 20.0:
            self.get_logger().warn(
                f"Depth không hợp lệ tại bbox center: {depth_value:.3f} m",
                throttle_duration_sec=2.0,
            )
            return None

        return depth_value

    def resolve_camera_frame(self, msg_frame_id):
        if self.camera_frame:
            return self.camera_frame
        if msg_frame_id:
            return msg_frame_id
        return "oakd_link"

    def publish_tf(self, x, y, z, stamp, frame_id):
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = frame_id
        t.child_frame_id = self.target_frame
        
        # Ánh xạ trục sang chuẩn ROS
        t.transform.translation.x = float(z)
        t.transform.translation.y = float(-x)
        t.transform.translation.z = float(-y)
        
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectLocalizationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
