#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
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
    """Bring up Nav2 together with perception, localization and mission logic."""

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_yaml_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("params_file")
    use_rviz = LaunchConfiguration("use_rviz")
    show_debug_window = LaunchConfiguration("show_debug_window")
    auto_initial_pose = LaunchConfiguration("auto_initial_pose")
    initial_pose_x = LaunchConfiguration("initial_pose_x")
    initial_pose_y = LaunchConfiguration("initial_pose_y")
    initial_pose_yaw = LaunchConfiguration("initial_pose_yaw")
    patrol_start_delay = LaunchConfiguration("patrol_start_delay")

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
                )
            )
        ],
    )

    oak_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_vision_oak"), "/launch/oak_detection.launch.py"]
        ),
        launch_arguments={"show_debug_window": show_debug_window}.items(),
    )

    object_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_object_localization"), "/launch/localization.launch.py"]
        )
    )

    mission_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_mission_manager"), "/launch/mission_manager.launch.py"]
        )
    )

    initial_pose_node = Node(
        package="tb4_bringup",
        executable="initial_pose_publisher",
        name="tb4_initial_pose_publisher",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"x": initial_pose_x},
            {"y": initial_pose_y},
            {"yaw": initial_pose_yaw},
            {"delay_sec": 8.0},
        ],
        condition=IfCondition(auto_initial_pose),
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
                default_value="true",
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
                "auto_initial_pose",
                default_value="true",
                description="Publish an AMCL initial pose automatically for simulation.",
            ),
            DeclareLaunchArgument(
                "initial_pose_x",
                default_value="0.0",
                description="Initial AMCL pose X in map frame.",
            ),
            DeclareLaunchArgument(
                "initial_pose_y",
                default_value="0.0",
                description="Initial AMCL pose Y in map frame.",
            ),
            DeclareLaunchArgument(
                "initial_pose_yaw",
                default_value="0.0",
                description="Initial AMCL yaw in radians.",
            ),
            DeclareLaunchArgument(
                "patrol_start_delay",
                default_value="35.0",
                description="Delay patrol start until AMCL/Nav2 TF is ready.",
            ),
            nav_localization_launch,
            nav2_launch,
            initial_pose_node,
            nav_patrol_launch,
            oak_detection_launch,
            object_localization_launch,
            mission_launch,
            rviz_node,
        ]
    )
