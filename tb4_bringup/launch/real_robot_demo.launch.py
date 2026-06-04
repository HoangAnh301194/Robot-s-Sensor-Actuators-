#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from tb4_bringup.launch_utils import (
    resolve_default_map,
    resolve_default_nav2_params,
    resolve_default_rviz_config,
)


def generate_launch_description():
    """Bring up the application stack for the real robot."""

    default_waypoints_file = os.path.join(
        get_package_share_directory("tb4_nav_patrol"),
        "config",
        "patrol_waypoints.yaml",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_yaml_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("params_file")
    use_rviz = LaunchConfiguration("use_rviz")
    show_debug_window = LaunchConfiguration("show_debug_window")
    image_topic = LaunchConfiguration("image_topic")
    depth_topic = LaunchConfiguration("depth_topic")
    camera_info_topic = LaunchConfiguration("camera_info_topic")
    camera_frame = LaunchConfiguration("camera_frame")
    waypoints_file = LaunchConfiguration("waypoints_file")
    patrol_start_delay = LaunchConfiguration("patrol_start_delay")
    patrol_start_enabled = LaunchConfiguration("patrol_start_enabled")

    nav_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("turtlebot4_navigation"), "/launch/localization.launch.py"]
        ),
        launch_arguments={
            "map": map_yaml_file,
            "use_sim_time": use_sim_time,
        }.items(),
    )
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("turtlebot4_navigation"), "/launch/nav2.launch.py"]
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "params_file": params_file,
        }.items(),
    )

    nav_patrol_launch = TimerAction(
        period=patrol_start_delay,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [FindPackageShare("tb4_nav_patrol"), "/launch/nav_patrol.launch.py"]
                ),
                launch_arguments={
                    "waypoints_file": waypoints_file,
                    "start_enabled": patrol_start_enabled,
                }.items(),
            )
        ],
    )

    oak_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_vision_oak"), "/launch/oak_detection.launch.py"]
        ),
        launch_arguments={
            "show_debug_window": show_debug_window,
            "image_topic": image_topic,
        }.items(),
    )

    object_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("tb4_object_localization"),
                "/launch/localization.launch.py",
            ]
        ),
        launch_arguments={
            "depth_topic": depth_topic,
            "camera_info_topic": camera_info_topic,
            "camera_frame": camera_frame,
        }.items(),
    )

    mission_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("tb4_mission_manager"),
                "/launch/mission_manager.launch.py",
            ]
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

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation clock.",
            ),
            DeclareLaunchArgument(
                "map",
                default_value=resolve_default_map(),
                description="Occupancy grid map used by Nav2.",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=resolve_default_nav2_params(),
                description="Nav2 parameters YAML file.",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="false",
                description="Start RViz for monitoring.",
            ),
            DeclareLaunchArgument(
                "show_debug_window",
                default_value="false",
                description="Show the OpenCV detection preview window.",
            ),
            DeclareLaunchArgument(
                "image_topic",
                default_value="/oakd/rgb/preview/image_raw",
                description="Real robot RGB image topic. Override after checking ros2 topic list.",
            ),
            DeclareLaunchArgument(
                "depth_topic",
                default_value="/oakd/rgb/preview/depth",
                description="Real robot depth image topic. Override after checking ros2 topic list.",
            ),
            DeclareLaunchArgument(
                "camera_info_topic",
                default_value="/oakd/rgb/preview/camera_info",
                description="Real robot CameraInfo topic. Override after checking ros2 topic list.",
            ),
            DeclareLaunchArgument(
                "camera_frame",
                default_value="oakd_link",
                description="Override camera frame if real OAK-D frame differs.",
            ),
            DeclareLaunchArgument(
                "waypoints_file",
                default_value=default_waypoints_file,
                description="Patrol YAML for the real robot. Edit it before running in a new area.",
            ),
            DeclareLaunchArgument(
                "patrol_start_delay",
                default_value="30.0",
                description="Delay patrol start so user can set AMCL initial pose in RViz.",
            ),
            DeclareLaunchArgument(
                "patrol_start_enabled",
                default_value="true",
                description="Enable patrol after patrol_start_delay.",
            ),
            nav_localization_launch,
            nav2_launch,
            nav_patrol_launch,
            oak_detection_launch,
            object_localization_launch,
            mission_launch,
            rviz_node,
        ]
    )
