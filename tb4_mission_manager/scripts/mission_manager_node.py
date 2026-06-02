#!/usr/bin/env python3

import rclpy
import math
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import tf2_ros

class MissionManagerNode(Node):
    def __init__(self):
        super().__init__('mission_manager_node')
        
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.subscription = self.create_subscription(
            PoseStamped,
            '/target_object_pose_map',
            self.object_callback,
            10)
            
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.safe_distance = 1.5
        self.get_logger().info("Mission Manager đã sẵn sàng!")

    def object_callback(self, msg):
        try:
            # Transform tọa độ vật thể từ khung camera (oakd_link) sang khung bản đồ (map)
            transform = self.tf_buffer.lookup_transform(
                'map', 
                msg.header.frame_id, # oakd_link
                rclpy.time.Time()
            )
            
            # Thực hiện phép biến đổi tọa độ (Pose Transformation)
            # Ở đây ta làm đơn giản hóa: cộng trực tiếp tọa độ robot (map) và vật thể (camera) 
            # (Chính xác phải dùng quaternion, nhưng để demo nhanh ta dùng giả định robot đi thẳng)
            
            robot_x = transform.transform.translation.x
            robot_y = transform.transform.translation.y
            
            # Tọa độ vật thể so với robot (từ localization node)
            obj_rel_x = msg.pose.position.x
            obj_rel_y = msg.pose.position.y
            
            # Tọa độ vật thể trong map (xấp xỉ)
            obj_map_x = robot_x + obj_rel_x
            obj_map_y = robot_y + obj_rel_y

            self.get_logger().info(f"Vật thể tại Map: ({obj_map_x:.2f}, {obj_map_y:.2f})")

            # Tính Safe Goal
            dist_to_obj = math.sqrt(obj_rel_x**2 + obj_rel_y**2)
            
            goal_map_x = obj_map_x
            goal_map_y = obj_map_y
            
            if dist_to_obj > self.safe_distance:
                ratio = (dist_to_obj - self.safe_distance) / dist_to_obj
                # Lùi lại một chút so với vật thể
                goal_map_x = robot_x + (obj_rel_x * ratio)
                goal_map_y = robot_y + (obj_rel_y * ratio)

            self.send_goal_to_nav2(goal_map_x, goal_map_y)

        except tf2_ros.TransformException as ex:
            self.get_logger().error(f"Lỗi transform tọa độ: {ex}")

    def send_goal_to_nav2(self, x, y):
        self.get_logger().info("Đang chờ Nav2 Action Server...")
        self.nav_client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f"Gửi Goal Nav2: ({x:.2f}, {y:.2f})")
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Nav2 từ chối Goal!')
            return

        self.get_logger().info('Nav2 đã chấp nhận Goal.')
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().status
        if result == 4:
            self.get_logger().info('ĐÃ ĐẾN ĐÍCH AN TOÀN!')

def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
