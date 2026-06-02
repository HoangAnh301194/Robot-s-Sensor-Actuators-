#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tb4_mission_manager',
            executable='mission_manager_node.py',
            name='mission_manager_node',
            output='screen',
            parameters=[
                {'safe_distance': 1.0},
                {'target_class': 'oak_object'}
            ]
        )
    ])
