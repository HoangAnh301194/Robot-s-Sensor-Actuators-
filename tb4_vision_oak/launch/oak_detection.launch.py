import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Tìm đường dẫn đến thư mục share của gói tb4_vision_oak sau khi build
    package_dir = get_package_share_directory('tb4_vision_oak')
    
    # 2. Định vị chính xác file camera_params.yaml trong thư mục config
    config_file_path = os.path.join(package_dir, 'config', 'camera_params.yaml')

    # 3. Cấu hình Node để khởi chạy
    detection_node = Node(
        package='tb4_vision_oak',          # Tên gói ROS 2
        executable='detection_node.py',    # Tên file script xử lý
        name='oakd_detection_node',        # Tên Node khi chạy (phải trùng với tên trong file yaml)
        parameters=[config_file_path],     # Nạp file cấu hình thông số
        output='screen'                    # Đẩy toàn bộ log/print ra màn hình terminal
    )

    # 4. Trả về đối tượng LaunchDescription chứa node vừa cấu hình
    return LaunchDescription([
        detection_node
    ])
