#!/usr/bin/env python3
import os
import cv2
import rclpy
import numpy as np
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class SimDetectionNode(Node):
    def __init__(self):
        super().__init__("oakd_detection_node")
        self.bridge = CvBridge()

        # Đường dẫn tuyệt đối chính xác dựa trên lệnh 'find' của bạn
        base_path = "/home/nhatnguyen/tb4_project_ab/src/Robot-s-Sensor-Actuators-/tb4_vision_oak/models"
        prototxt = os.path.join(base_path, "MobileNetSSD_deploy.prototxt")
        caffemodel = os.path.join(base_path, "MobileNetSSD_deploy.caffemodel")

        # Kiểm tra sự tồn tại của file trước khi nạp
        if not os.path.exists(prototxt) or not os.path.exists(caffemodel):
            self.get_logger().error(f"Lỗi: Không tìm thấy file tại {base_path}")
            return

        # Nạp mô hình AI
        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        self.CLASSES = [
            "background",
            "aeroplane",
            "bicycle",
            "bird",
            "boat",
            "bottle",
            "bus",
            "car",
            "cat",
            "chair",
            "cow",
            "diningtable",
            "dog",
            "horse",
            "motorbike",
            "person",
            "pottedplant",
            "sheep",
            "sofa",
            "train",
            "tvmonitor",
        ]

        # Subscribe tới topic ảnh của robot
        self.subscription = self.create_subscription(
            Image, "/oakd/rgb/preview/image_raw", self.image_callback, 10
        )
        self.get_logger().info("Node AI đã khởi động thành công!")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            h, w = cv_image.shape[:2]

            # Xử lý nhận diện
            blob = cv2.dnn.blobFromImage(
                cv2.resize(cv_image, (300, 300)), 0.007843, (300, 300), 127.5
            )
            self.net.setInput(blob)
            detections = self.net.forward()

            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    startX, startY, endX, endY = box.astype("int")

                    # Vẽ khung hình
                    cv2.rectangle(
                        cv_image, (startX, startY), (endX, endY), (0, 255, 0), 2
                    )
                    label = f"{self.CLASSES[idx]}: {confidence * 100:.2f}%"
                    cv2.putText(
                        cv_image,
                        label,
                        (startX, startY - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            cv2.imshow("TurtleBot 4 AI Detection", cv_image)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"Lỗi callback: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = SimDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
