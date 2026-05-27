#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch file for OAK-D object detection."""

    ld = LaunchDescription()

    # OAK-D camera node
    oakd_node = Node(
        package="depthai_ros",
        executable="camera_node",
        output="screen",
        parameters=[
            # camera config parameters
        ],
    )

    # Object detection node
    detection_node = Node(
        package="tb4_vision_oak",
        executable="detection_node.py",
        output="screen",
        # parameters=[...]
    )

    ld.add_action(oakd_node)
    ld.add_action(detection_node)

    return ld
