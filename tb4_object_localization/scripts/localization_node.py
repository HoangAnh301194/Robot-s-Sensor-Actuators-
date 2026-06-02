#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import tf2_ros
from geometry_msgs.msg import TransformStamped
import numpy as np

class ObjectLocalizationNode(Node):
    def __init__(self):
        super().__init__('object_localization_node')
        self.bridge = CvBridge()
        
        # Biến lưu thông số camera (Intrinsics)
        self.fx = self.fy = self.cx = self.cy = None
        
        # TF Broadcaster để phát tọa độ lên RViz
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Đăng ký nhận thông số Camera
        self.create_subscription(CameraInfo, '/oakd/rgb/preview/camera_info', self.camera_info_callback, 10)
        # Đăng ký nhận ảnh Chiều sâu (Depth)
        self.create_subscription(Image, '/oakd/rgb/preview/depth', self.depth_callback, 10)
        
        self.get_logger().info("Đã khởi động Node 3D Object Localization!")

    def camera_info_callback(self, msg):
        # Lấy các thông số tiêu cự và tâm quang học
        if self.fx is None:
            self.fx = msg.k[0]
            self.cx = msg.k[2]
            self.fy = msg.k[4]
            self.cy = msg.k[5]

    def depth_callback(self, msg):
        if self.fx is None:
            return # Đợi có thông số camera trước

        try:
            # Chuyển ROS Image thành mảng OpenCV
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            height, width = depth_image.shape

            # GIẢ LẬP: Coi vật thể nằm ở chính giữa khung hình
            u = int(width / 2)
            v = int(height / 2)

            # Lấy giá trị khoảng cách Z (tại pixel u, v)
            Z = depth_image[v, u] 
            
            # Bỏ qua nếu điểm đó bị lỗi đo lường (Z = 0 hoặc NaN)
            if Z <= 0 or np.isnan(Z):
                return

            # Chuyển đổi mm sang mét (tùy thuộc vào định dạng của OAK-D, thường là mm)
            Z_m = Z / 1000.0

            # Tính tọa độ 3D (X_c, Y_c, Z_c) theo mô hình Pinhole
            X_c = (u - self.cx) * Z_m / self.fx
            Y_c = (v - self.cy) * Z_m / self.fy
            Z_c = Z_m

            # Phát Tọa độ (TF) lên hệ thống
            self.publish_tf(X_c, Y_c, Z_c, msg.header.stamp)

        except Exception as e:
            self.get_logger().error(f"Lỗi xử lý Depth: {e}")

    def publish_tf(self, x, y, z, stamp):
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = 'oakd_link' # Gắn với hệ tọa độ của camera
        t.child_frame_id = 'detected_object_3d' # Tên của vật thể
        
        t.transform.translation.x = float(z)   # Chú ý: Trục X của ROS thường hướng tới trước
        t.transform.translation.y = float(-x)  # Trục Y hướng sang trái
        t.transform.translation.z = float(-y)  # Trục Z hướng lên trên

        # Không xoay (Quaternion mặc định)
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

if __name__ == '__main__':
    main()
