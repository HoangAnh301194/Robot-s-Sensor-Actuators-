#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import random

class ObjectLocalizationNode(Node):
    def __init__(self):
        super().__init__('object_localization_node')
        # Publisher gửi tọa độ vật thể trong hệ map
        self.publisher_ = self.create_publisher(PoseStamped, '/target_object_pose_map', 10)
        
        # Tạo một timer để thỉnh thoảng "giả vờ" tìm thấy vật thể (mỗi 10 giây)
        self.timer = self.create_timer(10.0, self.publish_mock_object)
        self.get_logger().info("Object Localization Mock Node đã sẵn sàng...")

    def publish_mock_object(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        
        # Tọa độ giả (ví dụ vật thể ở x=2.0, y=1.0 trên bản đồ)
        msg.pose.position.x = 2.0
        msg.pose.position.y = 1.0
        msg.pose.position.z = 0.0
        
        # Hướng giả (không quay)
        msg.pose.orientation.w = 1.0
        
        self.publisher_.publish(msg)
        self.get_logger().info(f"--- MOCK DATA: Đã phát hiện vật thể tại x={msg.pose.position.x}, y={msg.pose.position.y} ---")

def main(args=None):
    rclpy.init(args=args)
    node = ObjectLocalizationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
