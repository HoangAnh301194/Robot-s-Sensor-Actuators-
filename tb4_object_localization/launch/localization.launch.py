#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch file for 3D object localization."""

    ld = LaunchDescription()

    # Object localization node
    localization_node = Node(
        package="tb4_object_localization",
        executable="localization_node.py",
        output="screen",
        # parameters=[...]
    )

    ld.add_action(localization_node)

    return ld
