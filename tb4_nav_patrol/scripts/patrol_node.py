#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        
        # Tạo Action Client để giao tiếp với Nav2
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Danh sách các điểm tuần tra (x, y, w)
        self.waypoints = [
            (1.0, 0.0, 1.0),
            (1.0, 1.0, 1.0),
            (0.0, 1.0, 1.0),
            (0.0, 0.0, 1.0)
        ]
        self.current_wp_index = 0
        
        # Đợi Action Server của Nav2 sẵn sàng
        self.get_logger().info("Đang chờ Nav2 Action Server...")
        self.nav_client.wait_for_server()
        self.get_logger().info("Nav2 đã sẵn sàng! Bắt đầu tuần tra.")
        
        # Bắt đầu đi tới điểm đầu tiên
        self.send_next_goal()

    def send_next_goal(self):
        if self.current_wp_index >= len(self.waypoints):
            # Nếu đi hết danh sách thì quay lại điểm đầu tiên (Lặp vô hạn)
            self.current_wp_index = 0

        wp = self.waypoints[self.current_wp_index]
        self.get_logger().info(f"Đang đi tới Waypoint {self.current_wp_index}: x={wp[0]}, y={wp[1]}")
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = wp[0]
        goal_msg.pose.pose.position.y = wp[1]
        goal_msg.pose.pose.orientation.w = wp[2]
        
        # Gửi goal và cài đặt callback khi có kết quả
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Nav2 từ chối Waypoint này!")
            return

        self.get_logger().info("Nav2 đã chấp nhận Waypoint.")
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().status
        # Status: 4 là SUCCEEDED
        if result == 4:
            self.get_logger().info(f"Đã đến Waypoint {self.current_wp_index} thành công!")
        else:
            self.get_logger().warn(f"Chưa đến được Waypoint {self.current_wp_index} (Mã lỗi: {result})")
        
        # Tăng chỉ số để đi điểm tiếp theo
        self.current_wp_index += 1
        
        # Tạm dừng 2 giây trước khi đi điểm tiếp theo
        # Sử dụng timer để tránh block thread
        self.create_timer(2.0, self.delayed_next_goal)

    def delayed_next_goal(self):
        # Hủy timer này sau khi chạy 1 lần
        self.send_next_goal()
        return

def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
