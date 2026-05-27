#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

class DetectionNode(Node):
    """ROS 2 node for object detection using OAK-D."""
    
    def __init__(self):
        super().__init__('tb4_detection_node')
        self.get_logger().info("TB4 Detection node started")
    
    def detection_callback(self, msg):
        """Process detection results."""
        pass

def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
