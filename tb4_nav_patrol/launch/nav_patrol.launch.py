#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    package_dir = get_package_share_directory("tb4_nav_patrol")
    default_waypoints_file = os.path.join(
        package_dir, "config", "patrol_waypoints.yaml"
    )

    waypoints_file = LaunchConfiguration("waypoints_file")
    start_enabled = LaunchConfiguration("start_enabled")
    frame_id = LaunchConfiguration("frame_id")
    next_goal_delay_sec = LaunchConfiguration("next_goal_delay_sec")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "waypoints_file",
                default_value=default_waypoints_file,
                description="YAML file containing patrol waypoints.",
            ),
            DeclareLaunchArgument(
                "start_enabled",
                default_value="true",
                description="Start patrol immediately after Nav2 is available.",
            ),
            DeclareLaunchArgument(
                "frame_id",
                default_value="map",
                description="Frame used by patrol goals.",
            ),
            DeclareLaunchArgument(
                "next_goal_delay_sec",
                default_value="2.0",
                description="Delay between patrol waypoints.",
            ),
            Node(
                package="tb4_nav_patrol",
                executable="patrol_node",
                output="screen",
                parameters=[
                    waypoints_file,
                    {"start_enabled": start_enabled},
                    {"frame_id": frame_id},
                    {"next_goal_delay_sec": next_goal_delay_sec},
                ],
            ),
        ]
    )
