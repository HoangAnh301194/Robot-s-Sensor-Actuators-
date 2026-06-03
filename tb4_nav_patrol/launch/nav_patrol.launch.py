#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch file for patrol logic only.

    Nav2 is brought up by tb4_bringup so this launch keeps the module focused on
    waypoint patrol behavior.
    """

    return LaunchDescription(
        [
            Node(
                package="tb4_nav_patrol",
                executable="patrol_node",
                output="screen",
            )
        ]
    )
