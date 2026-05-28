#!/usr/bin/env python3
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class SimDetectionNode(Node):
    def __init__(self):
        super().__init__("oakd_sim_detection_node")
        self.bridge = CvBridge()

        # Đăng ký nhận dữ liệu từ camera ảo của TurtleBot 4 trong Gazebo
        # Lưu ý: Tên topic có thể là '/color/image' hoặc '/oakd/rgb/preview/image_raw' tùy cấu hình mô phỏng
        self.subscription = self.create_subscription(
            Image, "/color/image", self.image_callback, 10
        )

        self.get_logger().info("Node nhận diện ảnh (Mô phỏng) đã khởi động!")

    def image_callback(self, msg):
        try:
            # Chuyển đổi định dạng ảnh từ ROS 2 sang OpenCV (mảng numpy)
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # --- TẠI ĐÂY BẠN SẼ CHÈN CODE NHẬN DIỆN ---
            # Ví dụ: cv2.dnn.readNetFromONNX(...) để chạy model YOLO/MobileNet
            # Hiện tại mình sẽ chỉ hiển thị ảnh để xác nhận luồng dữ liệu thông suốt

            cv2.imshow("TurtleBot 4 Simulated Camera", cv_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Lỗi xử lý ảnh: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = SimDetectionNode()
    rclpy.spin(node)

    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
