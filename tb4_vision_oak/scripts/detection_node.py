#!/usr/bin/env python3
import os
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
<<<<<<< HEAD
from ultralytics import YOLO

from vision_msgs.msg import Detection2D, Detection2DArray
from ament_index_python.packages import get_package_share_directory
>>>>>>> origin/main

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

        # Lấy đường dẫn đến thư mục models
        package_share_directory = get_package_share_directory('tb4_vision_oak')
        models_path = os.path.join(package_share_directory, 'models')
        prototxt = os.path.join(models_path, "MobileNetSSD_deploy.prototxt")
        caffemodel = os.path.join(models_path, "MobileNetSSD_deploy.caffemodel")

        if not os.path.exists(prototxt) or not os.path.exists(caffemodel):
            self.get_logger().error(f"Lỗi: Không tìm thấy file model tại {models_path}")
            return

        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        self.CLASSES = [
            "background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person",
            "pottedplant", "sheep", "sofa", "train", "tvmonitor",
        ]

        # Publisher gửi kết quả nhận diện cho module Localization
        self.detection_pub = self.create_publisher(Detection2DArray, "/vision/detected_objects", 10)

        # Subscribe tới topic ảnh
        self.subscription = self.create_subscription(
            Image, "/oakd/rgb/preview/image_raw", self.image_callback, 10
        )
        self.get_logger().info("Node AI nhận diện đã khởi động và sẵn sàng gửi dữ liệu!")


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

            blob = cv2.dnn.blobFromImage(
                cv2.resize(cv_image, (300, 300)), 0.007843, (300, 300), 127.5
            )
            self.net.setInput(blob)
            detections = self.net.forward()

            # Tạo mảng chứa các đối tượng phát hiện được
            detection_array = Detection2DArray()
            detection_array.header = msg.header

            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    startX, startY, endX, endY = box.astype("int")

                    # Vẽ khung hình để quan sát
                    cv2.rectangle(cv_image, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    label = f"{self.CLASSES[idx]}: {confidence * 100:.2f}%"
                    cv2.putText(cv_image, label, (startX, startY - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Thêm vào mảng kết quả để gửi đi
                    det = Detection2D()
                    det.bbox.center.position.x = float((startX + endX) / 2)
                    det.bbox.center.position.y = float((startY + endY) / 2)
                    det.bbox.size_x = float(endX - startX)
                    det.bbox.size_y = float(endY - startY)
                    
                    # Gán nhãn (sử dụng class_id)
                    # Lưu ý: vision_msgs/Detection2D không có field label, thường dùng topic riêng hoặc custom msg
                    # Ở đây ta dùng kết quả để Localization xử lý
                    detection_array.detections.append(det)

            # Publish tọa độ 2D sang module Localization
            self.detection_pub.publish(detection_array)

            cv2.imshow("TurtleBot 4 AI Detection", cv_image)

            cv2.waitKey(1)
            
        except Exception as e:

            self.get_logger().error(f"Lỗi trong vòng callback nhận diện: {e}")

            self.get_logger().error(f"Lỗi callback: {e}")


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

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
