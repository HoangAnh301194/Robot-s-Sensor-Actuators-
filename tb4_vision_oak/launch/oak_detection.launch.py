import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = get_package_share_directory("tb4_vision_oak")
    config_file_path = os.path.join(package_dir, "config", "camera_params.yaml")
    show_debug_window = LaunchConfiguration("show_debug_window")
    publish_debug_image = LaunchConfiguration("publish_debug_image")
    image_topic = LaunchConfiguration("image_topic")
    detections_topic = LaunchConfiguration("detections_topic")
    debug_image_topic = LaunchConfiguration("debug_image_topic")

    detection_node = Node(
        package="tb4_vision_oak",
        executable="detection_node",
        name="oakd_detection_node",
        parameters=[
            config_file_path,
            {
                "show_debug_window": show_debug_window,
                "publish_debug_image": publish_debug_image,
                "image_topic": image_topic,
                "detections_topic": detections_topic,
                "debug_image_topic": debug_image_topic,
            },
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "show_debug_window",
                default_value="false",
                description="Hiển thị khung hình detection qua OpenCV.",
            ),
            DeclareLaunchArgument(
                "publish_debug_image",
                default_value="true",
                description="Publish ảnh debug đã vẽ bounding box lên /vision/debug_image.",
            ),
            detection_node,
        ]
    )
