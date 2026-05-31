#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import math

class MissionManagerNode(Node):
    def __init__(self):
        super().__init__('mission_manager_node')
        
        # Subscribe tọa độ vật thể
        self.subscription = self.create_subscription(
            PoseStamped,
            '/target_object_pose_map',
            self.object_callback,
            10)
            
        # Publisher gửi Goal cho Nav2 (giả định dùng topic đơn giản trước)
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        
        self.safe_distance = 0.5 # mét
        self.get_logger().info("Mission Manager đã sẵn sàng và đang đợi vật thể...")

    def object_callback(self, msg):
        obj_x = msg.pose.position.x
        obj_y = msg.pose.position.y
        
        self.get_logger().info(f"PHÁT HIỆN VẬT THỂ tại: x={obj_x:.2f}, y={obj_y:.2f}")
        
        # LOGIC: Tính toán Safe Goal (Tạm thời giả định robot đang ở gốc 0,0 để tính hướng)
        # Trong thực tế sẽ cần lấy vị trí robot hiện tại từ TF
        
        # Tính toán điểm dừng cách vật thể 0.5m (giả sử robot tiếp cận từ hướng gốc tọa độ)
        distance = math.sqrt(obj_x**2 + obj_y**2)
        if distance > self.safe_distance:
            ratio = (distance - self.safe_distance) / distance
            goal_x = obj_x * ratio
            goal_y = obj_y * ratio
        else:
            goal_x = obj_x
            goal_y = obj_y

        self.get_logger().info(f"==> Đã sinh SAFE GOAL: x={goal_x:.2f}, y={goal_y:.2f} (cách vật thể {self.safe_distance}m)")
        
        # Gửi Goal cho Nav2
        goal_msg = PoseStamped()
        goal_msg.header.stamp = self.get_clock().now().to_msg()
        goal_msg.header.frame_id = 'map'
        goal_msg.pose.position.x = goal_x
        goal_msg.pose.position.y = goal_y
        goal_msg.pose.orientation.w = 1.0
        
        self.goal_pub.publish(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
