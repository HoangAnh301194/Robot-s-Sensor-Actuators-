#!/usr/bin/env python3
import os
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics import YOLO

class SimDetectionNode(Node):
    def __init__(self):
        super().__init__("oakd_detection_node")
        self.bridge = CvBridge()

        # 1. Khai báo Parameter để tránh việc viết cứng đường dẫn trong code
        # Đường dẫn mặc định vẫn trỏ tới file của bạn để chạy được ngay
        default_path = "/home/nhatnguyen/tb4_project_ab/src/Robot-s-Sensor-Actuators-/tb4_vision_oak/models/yolov8n.pt"
        self.declare_parameter("model_path", default_path)
        
        # Lấy giá trị cấu hình từ parameter
        model_path = self.get_parameter("model_path").get_parameter_value().string_value

        # 2. Kiểm tra sự tồn tại của file trước khi nạp
        if not os.path.exists(model_path):
            self.get_logger().error(f"Lỗi: Không tìm thấy file mô hình tại: {model_path}")
            return

        # 3. Nạp mô hình AI YOLOv8
        self.get_logger().info(f"Đang nạp mô hình YOLOv8 từ: {model_path}")
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            self.get_logger().error(f"Không thể khởi tạo mô hình YOLOv8: {e}")
            return
        
        # 4. Subscribe tới topic ảnh của robot trong Gazebo
        self.subscription = self.create_subscription(
            Image, "/oakd/rgb/preview/image_raw", self.image_callback, 10
        )
        self.get_logger().info("Node AI YOLOv8 đã khởi động thành công!")

    def image_callback(self, msg):
        try:
            # Chuyển đổi dữ liệu ảnh ROS sang format OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Xử lý nhận diện bằng YOLOv8 (verbose=False để ẩn log thừa)
            results = self.model(cv_image, verbose=False)

            # Sử dụng hàm .plot() có sẵn để tự vẽ Bounding Box và Label lên ảnh
            annotated_frame = results[0].plot()

            # Hiển thị cửa sổ kết quả nhận diện
            cv2.imshow("TurtleBot 4 AI Detection - YOLOv8", annotated_frame)
            cv2.waitKey(1)
            
        except Exception as e:
            self.get_logger().error(f"Lỗi trong vòng callback nhận diện: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SimDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Đang tắt Node nhận diện AI...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
