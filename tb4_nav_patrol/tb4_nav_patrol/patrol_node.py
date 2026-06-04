#!/usr/bin/env python3

import math

from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool


class PatrolNode(Node):
    def __init__(self):
        super().__init__("patrol_node")

        self.declare_parameter("frame_id", "map")
        self.declare_parameter("start_enabled", True)
        self.declare_parameter("next_goal_delay_sec", 2.0)
        self.declare_parameter(
            "waypoints",
            [
                1.0, 0.0, 0.0,
                1.0, 1.0, 1.5708,
                0.0, 1.0, 3.1416,
                0.0, 0.0, -1.5708,
            ],
        )

        self.frame_id = str(self.get_parameter("frame_id").value)
        self.next_goal_delay_sec = float(self.get_parameter("next_goal_delay_sec").value)
        self.waypoints = self.load_waypoints()
        self.patrol_enabled = self.parse_bool(
            self.get_parameter("start_enabled").value
        )

        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self.create_subscription(
            Bool,
            "/mission_manager/patrol_enabled",
            self.patrol_control_callback,
            qos,
        )

        self.current_wp_index = 0
        self.current_goal_handle = None
        self.send_goal_future = None
        self.get_result_future = None
        self.cancel_goal_future = None
        self.next_goal_timer = None

        self.server_wait_timer = self.create_timer(1.0, self.try_start_patrol)
        self.get_logger().info("Patrol node đã sẵn sàng, đang chờ Nav2 Action Server...")

    @staticmethod
    def parse_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    def load_waypoints(self):
        values = list(self.get_parameter("waypoints").value)
        if len(values) < 3 or len(values) % 3 != 0:
            self.get_logger().warn(
                "Invalid waypoints parameter; using safe default waypoint at map origin."
            )
            return [(0.0, 0.0, 0.0)]

        waypoints = []
        for index in range(0, len(values), 3):
            waypoints.append(
                (float(values[index]), float(values[index + 1]), float(values[index + 2]))
            )
        return waypoints

    @staticmethod
    def yaw_to_quaternion(yaw):
        return math.sin(yaw / 2.0), math.cos(yaw / 2.0)

    def patrol_control_callback(self, msg):
        if msg.data == self.patrol_enabled:
            return

        self.patrol_enabled = msg.data
        if self.patrol_enabled:
            self.get_logger().info("Mission Manager cho phép tiếp tục tuần tra.")
            self.try_start_patrol()
            return

        self.get_logger().info("Mission Manager tạm dừng tuần tra để xử lý mục tiêu.")
        self.cancel_next_goal_timer()
        self.cancel_active_goal()

    def try_start_patrol(self):
        if not self.patrol_enabled:
            return
        if self.current_goal_handle is not None or self.send_goal_future is not None:
            return
        if not self.nav_client.wait_for_server(timeout_sec=0.1):
            return

        if self.server_wait_timer is not None:
            self.server_wait_timer.cancel()
            self.server_wait_timer = None

        self.send_next_goal()

    def send_next_goal(self):
        if not self.patrol_enabled:
            return
        if self.current_goal_handle is not None or self.send_goal_future is not None:
            return

        if self.current_wp_index >= len(self.waypoints):
            self.current_wp_index = 0

        waypoint = self.waypoints[self.current_wp_index]
        self.get_logger().info(
            f"Đang đi tới waypoint {self.current_wp_index}: x={waypoint[0]}, y={waypoint[1]}"
        )

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = self.frame_id
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = waypoint[0]
        goal_msg.pose.pose.position.y = waypoint[1]
        qz, qw = self.yaw_to_quaternion(waypoint[2])
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.send_goal_future = None

        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Lỗi gửi goal tuần tra: {exc}")
            self.schedule_next_goal()
            return

        if not goal_handle.accepted:
            self.get_logger().warn("Nav2 từ chối waypoint tuần tra.")
            self.schedule_next_goal()
            return

        self.current_goal_handle = goal_handle
        if not self.patrol_enabled:
            self.cancel_active_goal()
            return

        self.get_logger().info("Nav2 đã chấp nhận waypoint tuần tra.")
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        self.get_result_future = None
        self.current_goal_handle = None

        try:
            status = future.result().status
        except Exception as exc:
            self.get_logger().error(f"Lỗi nhận kết quả tuần tra: {exc}")
            status = GoalStatus.STATUS_UNKNOWN

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f"Đã đến waypoint {self.current_wp_index} thành công."
            )
            self.current_wp_index += 1
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("Waypoint hiện tại đã bị hủy để nhường cho mission manager.")
        else:
            self.get_logger().warn(
                f"Không đến được waypoint {self.current_wp_index} (status={status})."
            )

        if self.patrol_enabled:
            self.schedule_next_goal()

    def cancel_active_goal(self):
        if self.current_goal_handle is None or self.cancel_goal_future is not None:
            return

        self.cancel_goal_future = self.current_goal_handle.cancel_goal_async()
        self.cancel_goal_future.add_done_callback(self.cancel_done_callback)

    def cancel_done_callback(self, future):
        self.cancel_goal_future = None

        try:
            future.result()
            self.get_logger().info("Đã gửi yêu cầu hủy goal tuần tra hiện tại.")
        except Exception as exc:
            self.get_logger().warn(f"Không thể hủy goal tuần tra: {exc}")

    def schedule_next_goal(self):
        if not self.patrol_enabled:
            return
        if self.next_goal_timer is not None:
            return

        self.next_goal_timer = self.create_timer(
            self.next_goal_delay_sec, self.delayed_next_goal
        )

    def delayed_next_goal(self):
        self.cancel_next_goal_timer()
        self.send_next_goal()

    def cancel_next_goal_timer(self):
        if self.next_goal_timer is None:
            return

        self.next_goal_timer.cancel()
        self.next_goal_timer = None


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
