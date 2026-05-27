#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class PatrolNode(Node):
    """ROS 2 node for TB4 patrol logic."""
    
    def __init__(self):
        super().__init__('tb4_patrol_node')
        self.get_logger().info("TB4 Patrol node started")
    
    def main_loop(self):
        """Main loop for patrol logic."""
        pass

def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
