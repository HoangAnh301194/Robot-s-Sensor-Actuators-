#!/usr/bin/env python3
import numpy as np
import rclpy
import tf2_ros
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped, PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
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
        self.pose_pub = self.create_publisher(PoseStamped, "/target_object_pose_map", 10)

        # Đăng ký nhận thông số Camera
        self.create_subscription(
            CameraInfo, "/oakd/rgb/preview/camera_info", self.camera_info_callback, 10
        )
        # Đăng ký nhận ảnh Chiều sâu (Depth)
        self.create_subscription(
            Image, "/oakd/rgb/preview/depth", self.depth_callback, 10
        )
        # Đăng ký nhận kết quả nhận diện 2D từ module Vision
        self.create_subscription(
            Detection2DArray, "/vision/detected_objects", self.detection_callback, 10
        )

        # Biến lưu tọa độ (u, v) trung tâm vật thể phát hiện được
        self.detected_u = None
        self.detected_v = None

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
            det = msg.detections[0] # Ưu tiên vật thể đầu tiên (confidence cao nhất)
            self.detected_u = int(det.bbox.center.position.x)
            self.detected_v = int(det.bbox.center.position.y)
            # self.get_logger().info(f"Đã nhận diện vật thể tại: ({self.detected_u}, {self.detected_v})")
        else:
            self.detected_u = None
            self.detected_v = None

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

                # Lấy giá trị khoảng cách Z
                Z = depth_image[v, u]
                if Z <= 0 or np.isnan(Z):
                    return

                # Chuyển đổi mm sang mét
                Z_m = Z / 1000.0

                # Tính tọa độ 3D (Xc, Yc, Zc) theo mô hình Pinhole
                X_c = (u - self.cx) * Z_m / self.fx
                Y_c = (v - self.cy) * Z_m / self.fy
                Z_c = Z_m

                # 1. Publish TF (cho RViz2)
                self.publish_tf(X_c, Y_c, Z_c, msg.header.stamp)

                # 2. Publish Pose (cho Mission Manager)
                # Chuyển đổi từ tọa độ camera (Xc, Yc, Zc) sang tọa độ map theo chuẩn ROS
                pose_msg = PoseStamped()
                pose_msg.header = msg.header
                pose_msg.header.frame_id = "oakd_link"
                
                # Ánh xạ trục: X_cam -> Z_ros (sâu), Y_cam -> -X_ros (ngang), Z_cam -> -Y_ros (cao)
                # Lưu ý: Tọa độ này vẫn đang trong hệ quy chiếu của camera (oakd_link).
                # Để mission manager đi tới được, ta cần đổi sang hệ map (cần TF lookup), 
                # nhưng trong mô phỏng đơn giản, ta sẽ gửi tọa độ tương đối so với robot.
                pose_msg.pose.position.x = Z_c   # Tiến/Lùi
                pose_msg.pose.position.y = -X_c  # Trái/Phải
                pose_msg.pose.position.z = -Y_c  # Cao/Thấp
                pose_msg.pose.orientation.w = 1.0

                self.pose_pub.publish(pose_msg)

            except Exception as e:
                self.get_logger().error(f"Lỗi tính toán Depth: {e}")

    def publish_tf(self, x, y, z, stamp):
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = "oakd_link"
        t.child_frame_id = "detected_object_3d"
        
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
