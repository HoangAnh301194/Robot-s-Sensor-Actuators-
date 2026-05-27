#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Master launch file for real robot demo."""
    
    ld = LaunchDescription()
    
    # Nav2 + patrol
    nav_patrol_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('tb4_nav_patrol'),
            '/launch/nav_patrol.launch.py'
        ])
    )
    
    # OAK-D + detection
    oak_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('tb4_vision_oak'),
            '/launch/oak_detection.launch.py'
        ])
    )
    
    # Localization
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('tb4_object_localization'),
            '/launch/localization.launch.py'
        ])
    )
    
    # Mission manager
    mission_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('tb4_mission_manager'),
            '/launch/mission_manager.launch.py'
        ])
    )
    
    ld.add_action(nav_patrol_launch)
    ld.add_action(oak_detection_launch)
    ld.add_action(localization_launch)
    ld.add_action(mission_launch)
    
    return ld
