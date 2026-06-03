#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Master launch file to run Nav2 and Application logic on Laptop."""

    # 1. Khai báo các tham số
    use_sim_time = LaunchConfiguration('use_sim_time', default='false') # Set true nếu chạy Gazebo
    map_yaml_file = LaunchConfiguration('map', default=os.path.join(
        FindPackageShare('tb4_bringup').find('tb4_bringup'), 'maps', 'office.yaml'))

    # 2. Khởi chạy Nav2 (Navigation + Localization)
    # Lệnh này sẽ chạy AMCL, Map Server và các node điều hướng
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("nav2_bringup"), "/launch/bringup_launch.py"]
        ),
        launch_arguments={
            'map': map_yaml_file,
            'use_sim_time': use_sim_time,
            'params_file': os.path.join(FindPackageShare('tb4_bringup').find('tb4_bringup'), 'config', 'nav2_params.yaml')
        }.items(),
    )

    # 3. Các node logic của dự án
    nav_patrol_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_nav_patrol"), "/launch/nav_patrol.launch.py"]
        )
    )

    oak_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_vision_oak"), "/launch/oak_detection.launch.py"]
        )
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_object_localization"), "/launch/localization.launch.py"]
        )
    )

    mission_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("tb4_mission_manager"), "/launch/mission_manager.launch.py"]
        )
    )

    # 4. RViz2 để quan sát và set 2D Pose Estimate ban đầu
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(FindPackageShare('nav2_bringup').find('nav2_bringup'), 'rviz', 'nav2_default_view.rviz')]
    )

    ld = LaunchDescription()
    ld.add_action(nav2_launch)
    ld.add_action(nav_patrol_launch)
    ld.add_action(oak_detection_launch)
    ld.add_action(localization_launch)
    ld.add_action(mission_launch)
    ld.add_action(rviz_node)

    return ld
