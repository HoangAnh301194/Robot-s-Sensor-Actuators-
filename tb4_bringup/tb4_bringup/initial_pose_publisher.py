#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node

class InitialPosePublisher(Node):
    def __init__(self):
        super().__init__('tb4_initial_pose_publisher')
        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('yaw', 0.0)
        self.declare_parameter('delay_sec', 8.0)
        self.declare_parameter('publish_count', 20)

        self.publisher = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.publish_count = int(self.get_parameter('publish_count').value)
        self.sent_count = 0
        delay_sec = float(self.get_parameter('delay_sec').value)
        self.start_timer = self.create_timer(delay_sec, self.start_publishing)
        self.publish_timer = None
        self.get_logger().info(f'Will publish AMCL initial pose after {delay_sec:.1f}s')

    def start_publishing(self):
        self.start_timer.cancel()
        self.publish_timer = self.create_timer(0.2, self.publish_initial_pose)

    def publish_initial_pose(self):
        if self.sent_count >= self.publish_count:
            self.get_logger().info('Initial pose published; shutting down helper node.')
            rclpy.shutdown()
            return

        x = float(self.get_parameter('x').value)
        y = float(self.get_parameter('y').value)
        yaw = float(self.get_parameter('yaw').value)

        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
        msg.pose.covariance[0] = 0.25
        msg.pose.covariance[7] = 0.25
        msg.pose.covariance[35] = 0.068

        self.publisher.publish(msg)
        self.sent_count += 1

def main(args=None):
    rclpy.init(args=args)
    node = InitialPosePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
