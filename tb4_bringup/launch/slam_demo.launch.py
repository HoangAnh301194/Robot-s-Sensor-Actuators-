#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Launch file for SLAM mapping."""

    # 1. Khai báo tham số
    use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true",
        description="Use simulation clock"
    )

    # 2. Khởi chạy SLAM Toolbox (Online Async)
    # Đây là node chính để tạo bản đồ từ Lidar
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("slam_toolbox"), "/launch/online_async_launch.py"]
        ),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    # 3. Khởi chạy các module Vision & Localization (vẫn chạy được khi SLAM)
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

    # 4. RViz2 để quan sát bản đồ đang được xây dựng
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(FindPackageShare("nav2_bringup").find("nav2_bringup"), "rviz", "nav2_default_view.rviz")]
    )

    ld = LaunchDescription()
    ld.add_action(use_sim_time)
    ld.add_action(slam_launch)
    ld.add_action(oak_detection_launch)
    ld.add_action(localization_launch)
    ld.add_action(rviz_node)

    return ld
