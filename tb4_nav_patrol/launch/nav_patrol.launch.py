#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch file for TB4 Navigation2 patrol."""

    ld = LaunchDescription()

    # Navigation2 node
    nav2_node = Node(
        package="nav2_bringup",
        executable="bringup_launch.py",
        output="screen",
        # parameters=[...]
    )

    # Patrol logic node
    patrol_node = Node(
        package="tb4_nav_patrol",
        executable="patrol_node.py",
        output="screen",
    )

    ld.add_action(nav2_node)
    ld.add_action(patrol_node)

    return ld
