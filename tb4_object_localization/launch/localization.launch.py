#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch file for 3D object localization."""

    config_file = os.path.join(
        get_package_share_directory("tb4_object_localization"),
        "config",
        "localization.yaml",
    )

    localization_node = Node(
        package="tb4_object_localization",
        executable="localization_node.py",
        name="object_localization",
        output="screen",
        parameters=[config_file],
    )

    return LaunchDescription([
        localization_node,
    ])