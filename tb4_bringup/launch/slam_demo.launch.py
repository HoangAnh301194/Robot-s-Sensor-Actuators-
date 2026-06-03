#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from tb4_bringup.launch_utils import resolve_default_rviz_config

def generate_launch_description():
    """Launch file for SLAM mapping."""

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock",
    )
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="false",
        description="Start RViz for monitoring.",
    )
    show_debug_window_arg = DeclareLaunchArgument(
        "show_debug_window",
        default_value="false",
        description="Show the OpenCV detection preview window.",
    )
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_rviz = LaunchConfiguration("use_rviz")
    show_debug_window = LaunchConfiguration("show_debug_window")

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("slam_toolbox"), "/launch/online_async_launch.py"]
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    oak_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_vision_oak"), "/launch/oak_detection.launch.py"]
        ),
        launch_arguments={"show_debug_window": show_debug_window}.items(),
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_object_localization"), "/launch/localization.launch.py"]
        )
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", resolve_default_rviz_config()],
        condition=IfCondition(use_rviz),
    )

    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(use_rviz_arg)
    ld.add_action(show_debug_window_arg)
    ld.add_action(slam_launch)
    ld.add_action(oak_detection_launch)
    ld.add_action(localization_launch)
    ld.add_action(rviz_node)

    return ld
