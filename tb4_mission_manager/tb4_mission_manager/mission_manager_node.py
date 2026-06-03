#!/usr/bin/env python3

import math

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from std_msgs.msg import Bool
import tf2_ros


class MissionManagerNode(Node):
    def __init__(self):
        super().__init__("mission_manager_node")

        self.declare_parameter("safe_distance", 1.0)
        self.declare_parameter("target_cooldown_sec", 5.0)

        self.safe_distance = float(self.get_parameter("safe_distance").value)
        self.target_cooldown_sec = float(
            self.get_parameter("target_cooldown_sec").value
        )

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self.patrol_control_pub = self.create_publisher(
            Bool, "/mission_manager/patrol_enabled", qos
        )
        self.create_subscription(
            PoseStamped, "/target_object_pose_map", self.object_callback, 10
        )

        self.active_goal_handle = None
        self.send_goal_future = None
        self.get_result_future = None
        self.state = "patrolling"
        self.ignore_targets_until = self.get_clock().now()

        self.publish_patrol_enabled(True)
        self.get_logger().info("Mission Manager đã sẵn sàng.")

    def object_callback(self, msg):
        if self.state != "patrolling":
            return
        if self.get_clock().now() < self.ignore_targets_until:
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                "map",
                msg.header.frame_id,
                Time(),
                timeout=Duration(seconds=0.2),
            )
        except tf2_ros.TransformException as exc:
            self.get_logger().warn(f"Chưa transform được mục tiêu sang map: {exc}")
            return

        rel_x = msg.pose.position.x
        rel_y = msg.pose.position.y
        rel_z = msg.pose.position.z
        planar_distance = math.hypot(rel_x, rel_y)

        if planar_distance <= self.safe_distance:
            return

        robot_x = transform.transform.translation.x
        robot_y = transform.transform.translation.y
        map_dx, map_dy, _ = self.rotate_vector_by_quaternion(
            rel_x,
            rel_y,
            rel_z,
            transform.transform.rotation.x,
            transform.transform.rotation.y,
            transform.transform.rotation.z,
            transform.transform.rotation.w,
        )
        obj_map_x = robot_x + map_dx
        obj_map_y = robot_y + map_dy

        approach_distance = math.hypot(map_dx, map_dy)
        if approach_distance <= self.safe_distance:
            return

        ratio = (approach_distance - self.safe_distance) / approach_distance
        goal_map_x = robot_x + (map_dx * ratio)
        goal_map_y = robot_y + (map_dy * ratio)

        self.publish_patrol_enabled(False)
        self.state = "approaching_target"
        self.send_goal_to_nav2(goal_map_x, goal_map_y)

    def send_goal_to_nav2(self, x, y):
        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("Nav2 Action Server chưa sẵn sàng.")
            self.restore_patrol()
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f"Gửi goal tiếp cận an toàn: ({x:.2f}, {y:.2f})")
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.send_goal_future = None

        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Lỗi gửi goal tới Nav2: {exc}")
            self.restore_patrol()
            return

        if not goal_handle.accepted:
            self.get_logger().warn("Nav2 từ chối goal tiếp cận.")
            self.restore_patrol()
            return

        self.active_goal_handle = goal_handle
        self.get_logger().info("Nav2 đã chấp nhận goal tiếp cận.")
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        self.get_result_future = None
        self.active_goal_handle = None

        try:
            status = future.result().status
        except Exception as exc:
            self.get_logger().error(f"Lỗi nhận kết quả mission: {exc}")
            status = GoalStatus.STATUS_UNKNOWN

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Đã đến vị trí tiếp cận an toàn.")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn("Goal tiếp cận đã bị hủy.")
        else:
            self.get_logger().warn(f"Mission kết thúc với status={status}.")

        self.restore_patrol()

    def restore_patrol(self):
        self.state = "patrolling"
        self.ignore_targets_until = self.get_clock().now() + Duration(
            seconds=self.target_cooldown_sec
        )
        self.publish_patrol_enabled(True)

    def publish_patrol_enabled(self, enabled):
        msg = Bool()
        msg.data = enabled
        self.patrol_control_pub.publish(msg)

    @staticmethod
    def rotate_vector_by_quaternion(x, y, z, qx, qy, qz, qw):
        xx = qx * qx
        yy = qy * qy
        zz = qz * qz
        xy = qx * qy
        xz = qx * qz
        yz = qy * qz
        wx = qw * qx
        wy = qw * qy
        wz = qw * qz

        rot_x = (1.0 - 2.0 * (yy + zz)) * x + 2.0 * (xy - wz) * y + 2.0 * (
            xz + wy
        ) * z
        rot_y = 2.0 * (xy + wz) * x + (1.0 - 2.0 * (xx + zz)) * y + 2.0 * (
            yz - wx
        ) * z
        rot_z = 2.0 * (xz - wy) * x + 2.0 * (yz + wx) * y + (1.0 - 2.0 * (xx + yy)) * z
        return rot_x, rot_y, rot_z


def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
