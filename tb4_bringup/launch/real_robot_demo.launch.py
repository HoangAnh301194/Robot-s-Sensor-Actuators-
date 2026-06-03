#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
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

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_yaml_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("params_file")
    use_rviz = LaunchConfiguration("use_rviz")
    show_debug_window = LaunchConfiguration("show_debug_window")

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

    nav_patrol_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_nav_patrol"), "/launch/nav_patrol.launch.py"]
        )
    )

    oak_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_vision_oak"), "/launch/oak_detection.launch.py"]
        ),
        launch_arguments={"show_debug_window": show_debug_window}.items(),
    )

    object_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("tb4_object_localization"),
                "/launch/localization.launch.py",
            ]
        )
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
            nav_localization_launch,
            nav2_launch,
            nav_patrol_launch,
            oak_detection_launch,
            object_localization_launch,
            mission_launch,
            rviz_node,
        ]
    )
