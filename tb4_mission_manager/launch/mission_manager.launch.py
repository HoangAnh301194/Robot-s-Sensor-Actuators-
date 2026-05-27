#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """Launch file for mission management."""
    
    ld = LaunchDescription()
    
    # Mission manager node
    mission_node = Node(
        package='tb4_mission_manager',
        executable='mission_manager_node.py',
        output='screen',
        # parameters=[...]
    )
    
    ld.add_action(mission_node)
    
    return ld
