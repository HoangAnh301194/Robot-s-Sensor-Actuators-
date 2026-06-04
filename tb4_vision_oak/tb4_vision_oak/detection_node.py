#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics import YOLO
from vision_msgs.msg import (
    Detection2D,
    Detection2DArray,
    ObjectHypothesisWithPose,
)


class SimDetectionNode(Node):
    def __init__(self):
        super().__init__("oakd_detection_node")
        self.bridge = CvBridge()

        self.declare_parameter("confidence_threshold", 0.5)
        self.declare_parameter("show_debug_window", False)
        self.declare_parameter("publish_debug_image", True)
        self.declare_parameter("image_topic", "/oakd/rgb/preview/image_raw")
        self.declare_parameter("detections_topic", "/vision/detected_objects")
        self.declare_parameter("debug_image_topic", "/vision/debug_image")

        self.confidence_threshold = float(
            self.get_parameter("confidence_threshold").value
        )
        self.show_debug_window = bool(self.get_parameter("show_debug_window").value)
        self.publish_debug_image = bool(self.get_parameter("publish_debug_image").value)
        self.image_topic = str(self.get_parameter("image_topic").value)
        self.detections_topic = str(self.get_parameter("detections_topic").value)
        self.debug_image_topic = str(self.get_parameter("debug_image_topic").value)
        self.window_enabled = self.show_debug_window and bool(os.environ.get("DISPLAY"))
        if self.show_debug_window and not self.window_enabled:
            self.get_logger().warn(
                "show_debug_window=true nhưng không có DISPLAY, sẽ chạy không hiển thị."
            )

        # ── Load YOLOv8 model ──────────────────────────────────────────
        package_share_directory = get_package_share_directory("tb4_vision_oak")
        local_model = os.path.join(package_share_directory, "models", "yolov8n.pt")
        model_path = local_model if os.path.exists(local_model) else "yolov8n.pt"

        self.get_logger().info(f"Đang tải model YOLO từ: {model_path}")
        self.model = YOLO(model_path)
        self.class_names = self.model.names  # dict {0: 'person', 1: 'bicycle', ...}
        self.get_logger().info(
            f"Model YOLO đã tải xong — {len(self.class_names)} classes."
        )

        # ── ROS publishers / subscribers ───────────────────────────────
        self.detection_pub = self.create_publisher(
            Detection2DArray, self.detections_topic, 10
        )
        self.debug_image_pub = self.create_publisher(Image, self.debug_image_topic, 10)
        self.subscription = self.create_subscription(
            Image, self.image_topic, self.image_callback, 10
        )
        self.get_logger().info("Node AI nhận diện (YOLOv8) đã khởi động.")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # ── Inference ──────────────────────────────────────────────
            results = self.model.predict(
                cv_image,
                conf=self.confidence_threshold,
                verbose=False,
            )
            result = results[0]
            boxes = result.boxes  # ultralytics Boxes object

            # ── Build Detection2DArray ─────────────────────────────────
            detection_array = Detection2DArray()
            detection_array.header = msg.header

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                det = Detection2D()
                det.bbox.center.position.x = (x1 + x2) / 2.0
                det.bbox.center.position.y = (y1 + y2) / 2.0
                det.bbox.size_x = float(x2 - x1)
                det.bbox.size_y = float(y2 - y1)

                # Thêm thông tin class và confidence
                hyp = ObjectHypothesisWithPose()
                hyp.hypothesis.class_id = str(class_id)
                hyp.hypothesis.score = confidence
                det.results.append(hyp)

                detection_array.detections.append(det)

            self.detection_pub.publish(detection_array)

            # ── Debug visualisation ────────────────────────────────────
            if self.publish_debug_image or self.window_enabled:
                # ultralytics cung cấp ảnh đã vẽ bbox + label sẵn
                debug_frame = result.plot()

                if self.publish_debug_image:
                    debug_msg = self.bridge.cv2_to_imgmsg(debug_frame, encoding="bgr8")
                    debug_msg.header = msg.header
                    self.debug_image_pub.publish(debug_msg)

                if self.window_enabled:
                    self.show_debug_image(debug_frame)

        except Exception as exc:
            self.get_logger().error(f"Lỗi callback detection: {exc}")

    def show_debug_image(self, cv_image):
        try:
            cv2.imshow("TurtleBot 4 AI Detection", cv_image)
            cv2.waitKey(1)
        except cv2.error as exc:
            self.window_enabled = False
            self.get_logger().warn(
                "Không thể mở cửa sổ OpenCV debug. "
                "Hãy chạy show_debug_window:=false hoặc cài OpenCV có GUI backend "
                f"(GTK/Qt). Chi tiết: {exc}"
            )


def main(args=None):
    rclpy.init(args=args)
    node = SimDetectionNode()
    try:
        rclpy.spin(node)
    finally:
        if node.window_enabled:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
