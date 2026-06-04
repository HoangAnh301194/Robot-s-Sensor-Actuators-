#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    camera_info_topic = LaunchConfiguration("camera_info_topic")
    depth_topic = LaunchConfiguration("depth_topic")
    detections_topic = LaunchConfiguration("detections_topic")
    target_pose_topic = LaunchConfiguration("target_pose_topic")
    marker_topic = LaunchConfiguration("marker_topic")
    camera_frame = LaunchConfiguration("camera_frame")
    target_frame = LaunchConfiguration("target_frame")

    localization_node = Node(
        package="tb4_object_localization",
        executable="localization_node.py",
        output="screen",
        parameters=[
            {"camera_info_topic": camera_info_topic},
            {"depth_topic": depth_topic},
            {"detections_topic": detections_topic},
            {"target_pose_topic": target_pose_topic},
            {"marker_topic": marker_topic},
            {"camera_frame": camera_frame},
            {"target_frame": target_frame},
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "camera_info_topic",
                default_value="/oakd/rgb/preview/camera_info",
                description="CameraInfo topic for RGB-D camera.",
            ),
            DeclareLaunchArgument(
                "depth_topic",
                default_value="/oakd/rgb/preview/depth",
                description="Depth image topic for RGB-D camera.",
            ),
            DeclareLaunchArgument(
                "detections_topic",
                default_value="/vision/detected_objects",
                description="Detection2DArray input topic.",
            ),
            DeclareLaunchArgument(
                "target_pose_topic",
                default_value="/target_object_pose_map",
                description="Target pose output topic.",
            ),
            DeclareLaunchArgument(
                "marker_topic",
                default_value="/target_object_marker",
                description="RViz marker output topic.",
            ),
            DeclareLaunchArgument(
                "camera_frame",
                default_value="oakd_link",
                description="Camera frame used for target pose. Override if real OAK-D frame differs.",
            ),
            DeclareLaunchArgument(
                "target_frame",
                default_value="detected_object_3d",
                description="TF child frame for detected target.",
            ),
            localization_node,
        ]
    )
