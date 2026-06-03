#!/usr/bin/env python3
import os
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics import YOLO
from vision_msgs.msg import Detection2D, Detection2DArray


class SimDetectionNode(Node):

    def __init__(self):
        super().__init__("oakd_detection_node")
        self.bridge = CvBridge()

        # Tách dòng đường dẫn quá dài để đạt chuẩn linter
        base_path = (
            "/home/nhatnguyen/tb4_project_ab/src/"
            "Robot-s-Sensor-Actuators-/tb4_vision_oak/models/yolov8n.pt"
        )
        self.declare_parameter("model_path", base_path)
        
        # Lấy giá trị cấu hình từ parameter
        model_param = self.get_parameter("model_path")
        model_path = model_param.get_parameter_value().string_value

        # Kiểm tra sự tồn tại của file trước khi nạp
        if not os.path.exists(model_path):
            self.get_logger().error(
                f"Lỗi: Không tìm thấy file mô hình tại: {model_path}"
            )
            return

        # Nạp mô hình AI YOLOv8
        self.get_logger().info(f"Đang nạp mô hình YOLOv8 từ: {model_path}")
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            self.get_logger().error(
                f"Không thể khởi tạo mô hình YOLOv8: {e}"
            )
            return
        
        # Publisher gửi kết quả nhận diện cho module Localization
        self.detection_pub = self.create_publisher(
            Detection2DArray, "/vision/detected_objects", 10
        )

        # Subscribe tới topic ảnh của robot trong Gazebo
        self.subscription = self.create_subscription(
            Image, "/oakd/rgb/preview/image_raw", self.image_callback, 10
        )
        self.get_logger().info(
            "Node AI YOLOv8 đã khởi động và sẵn sàng gửi dữ liệu!"
        )

    def image_callback(self, msg):
        try:
            # Chuyển đổi dữ liệu ảnh ROS sang format OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Xử lý nhận diện bằng YOLOv8
            results = self.model(cv_image, verbose=False)

            # Tạo mảng chứa các đối tượng phát hiện được
            detection_array = Detection2DArray()
            detection_array.header = msg.header

            # Trích xuất dữ liệu Bounding Box từ kết quả YOLOv8
            for box in results[0].boxes:
                confidence = float(box.conf[0])
                if confidence > 0.5:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    det = Detection2D()
                    det.bbox.center.position.x = float((x1 + x2) / 2.0)
                    det.bbox.center.position.y = float((y1 + y2) / 2.0)
                    det.bbox.size_x = float(x2 - x1)
                    det.bbox.size_y = float(y2 - y1)
                    
                    detection_array.detections.append(det)

            # Publish tọa độ 2D sang module Localization
            self.detection_pub.publish(detection_array)

            # Tự vẽ Bounding Box và Label lên ảnh để xem trực quan
            annotated_frame = results[0].plot()

            # Hiển thị cửa sổ kết quả nhận diện
            cv2.imshow("TurtleBot 4 AI Detection - YOLOv8", annotated_frame)
            cv2.waitKey(1)
            
        except Exception as e:
            self.get_logger().error(
                f"Lỗi trong vòng callback nhận diện: {e}"
            )


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
