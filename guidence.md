# TurtleBot4 Simulation Run Guide

Tài liệu này dùng để setup, test từng module, debug visualization và chạy full mission cho project `Robots_Sensor_Actuators`.

## 1. Quy ước terminal

Mỗi terminal mới nên chạy:

```bash
unset ROS_DOMAIN_ID
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash
```

Nếu cần multi-robot mới dùng `ROS_DOMAIN_ID`, nhưng tất cả terminal phải dùng cùng một ID:

```bash
export ROS_DOMAIN_ID=1
```

## 2. Build workspace

```bash
cd ~/tb4_project_ab
source /opt/ros/humble/setup.bash
PYTHONNOUSERSITE=1 colcon build --symlink-install
source install/setup.bash
```

Nếu repo có `venv`, chặn `colcon` quét nhầm package trong virtualenv:

```bash
touch /media/hoang_anh/5A1479B014798FAD/Robots_Sensor_Actuators/venv/COLCON_IGNORE
```

Kiểm tra package:

```bash
ros2 pkg list | grep '^tb4'
```

## 3. Chạy simulator TurtleBot4

Mở terminal 1:

```bash
unset ROS_DOMAIN_ID
unset LIBGL_ALWAYS_SOFTWARE
export QT_QPA_PLATFORM=xcb
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py model:=lite world:=warehouse
```

Nên dùng `warehouse` trước vì nhẹ hơn `depot`. Đợi 30-60 giây cho Gazebo/Ignition load xong.

Mở terminal 2 kiểm tra simulator có dữ liệu thật:

```bash
unset ROS_DOMAIN_ID
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 topic hz /clock
ros2 topic hz /scan
ros2 topic echo /clock --once
ros2 topic echo /scan --once
```

Kỳ vọng:

- `/clock` có rate.
- `/scan` có rate khoảng 15-20 Hz.
- `echo /scan --once` in ra `ranges`.

Nếu topic có trong list nhưng không có data/rate, dọn process Gazebo rồi chạy lại:

```bash
pkill -9 -f "ign gazebo"
pkill -9 -f "ros2 launch turtlebot4_ignition_bringup"
pkill -9 -f "parameter_bridge"
```

## 4. Test từng module riêng lẻ

Giữ simulator ở terminal 1 đang chạy. Mỗi module nên mở terminal riêng.

### 4.1 Vision Detection

```bash
ros2 launch tb4_vision_oak oak_detection.launch.py show_debug_window:=false
```

Module luôn dùng mặc định `yolov8n.pt`. Nếu `tb4_vision_oak/models/yolov8n.pt` tồn tại thì node dùng file local; nếu chưa có, Ultralytics sẽ tự download lần đầu chạy.

Debug/check:

```bash
ros2 topic list | grep vision
ros2 topic hz /vision/detected_objects
ros2 topic echo /vision/detected_objects --once
```

Bật cửa sổ OpenCV debug:

```bash
ros2 launch tb4_vision_oak oak_detection.launch.py show_debug_window:=true
```

Nếu OpenCV báo lỗi `cvShowImage` hoặc HighGUI chưa có GTK/Qt backend, hãy dùng `show_debug_window:=false` và xem ảnh bằng RViz `Image`, hoặc cài OpenCV có GUI backend thay vì bản headless.

### 4.2 Object Localization

Giữ detection node đang chạy, mở terminal khác:

```bash
ros2 launch tb4_object_localization localization.launch.py
```

Debug/check:

```bash
ros2 topic hz /oakd/rgb/preview/image_raw
ros2 topic hz /oakd/rgb/preview/depth
ros2 topic echo /oakd/rgb/preview/camera_info --once
ros2 topic list | grep target
ros2 topic echo /target_object_pose_map --once
```

Lưu ý: `/target_object_pose_map` chỉ publish khi detection tìm thấy object và depth hợp lệ.

### 4.3 Nav2 Localization

```bash
ros2 launch turtlebot4_navigation localization.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/warehouse.yaml \
  use_sim_time:=true
```

### 4.4 Nav2 Bringup

```bash
ros2 launch turtlebot4_navigation nav2.launch.py use_sim_time:=true
```

Debug/check:

```bash
ros2 action list | grep navigate
```

Kỳ vọng có:

```text
/navigate_to_pose
```

### 4.5 Mission Manager

Chỉ test mission đầy đủ sau khi Nav2 action server đã sẵn sàng. Nếu chỉ kiểm tra node khởi động thì có thể chạy trước Nav2, nhưng mission sẽ chưa gửi goal được.

```bash
ros2 launch tb4_mission_manager mission_manager.launch.py
```

Debug/check:

```bash
ros2 topic list | grep mission
ros2 topic echo /mission_manager/patrol_enabled
```

### 4.6 Patrol Node

Chỉ chạy sau khi Nav2 đã sẵn sàng:

```bash
ros2 launch tb4_nav_patrol nav_patrol.launch.py
```

Nếu không còn kẹt ở log chờ `Nav2 Action Server`, patrol đã kết nối được Nav2.

## 5. Visualization bằng RViz

Có thể chạy RViz riêng:

```bash
rviz2
```

Trong RViz thêm các display sau để debug:

- `Map`: topic `/map`
- `LaserScan`: topic `/scan`
- `TF`: xem cây frame `map -> odom -> base_link` và camera/object frames
- `Image`: topic `/oakd/rgb/preview/image_raw`
- `Image`: topic `/vision/debug_image` để xem ảnh đã vẽ bounding box detection
- `Pose`: topic `/target_object_pose_map`
- `Path`: các topic plan của Nav2 nếu cần debug đường đi

Project có sẵn dashboard RViz debug:

```bash
rviz2 -d ~/tb4_project_ab/src/Robots_Sensor_Actuators/tb4_bringup/rviz/tb4_debug.rviz
```

Khi chạy `tb4_bringup` với `use_rviz:=true`, dashboard này sẽ được mở mặc định.

Lưu ý:

- Warning `No map received` là bình thường nếu chưa chạy SLAM hoặc chưa chạy localization với file map.
- Khi đang chạy SLAM, kiểm tra map bằng `ros2 topic info /map` và `ros2 topic echo /map --once`. Nếu dashboard đã được cập nhật, hãy đóng RViz cũ và mở lại để nạp config mới.
- Với laser, chọn topic `/scan`. Các topic scan khác thường là sensor nội bộ như cliff/IR/rplidar raw.

Nếu chạy launch tổng với `use_rviz:=true`, RViz sẽ tự mở:

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/warehouse.yaml \
  use_sim_time:=true \
  use_rviz:=true \
  show_debug_window:=false
```

## 6. Chạy full mission/toàn bộ project

Điều kiện trước khi chạy full:

- Simulator đang chạy và `/clock`, `/scan`, `/odom`, `/tf` có data.
- Camera topics `/oakd/rgb/preview/image_raw`, `/oakd/rgb/preview/depth`, `/oakd/rgb/preview/camera_info` tồn tại.
- Workspace đã build và source.

Chạy full stack:

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/warehouse.yaml \
  use_sim_time:=true \
  use_rviz:=true \
  show_debug_window:=false
```

Bật cả OpenCV detection window:

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/warehouse.yaml \
  use_sim_time:=true \
  use_rviz:=true \
  show_debug_window:=true
```

Nếu đã tạo map riêng bằng SLAM, đổi `map:=...`:

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=$HOME/maps/office.yaml \
  use_sim_time:=true \
  use_rviz:=true
```

## 7. Mapping bằng SLAM

Chạy simulator trước, sau đó:

```bash
ros2 launch tb4_bringup slam_demo.launch.py use_sim_time:=true use_rviz:=true
```

Khi chưa có map, SLAM sẽ tự tạo topic `/map`. Di chuyển robot để quét môi trường bằng RViz `2D Goal Pose` hoặc teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Trong RViz, display `Map /map` sẽ hiện dần vùng đã quét. Nếu chưa thấy, kiểm tra:

```bash
ros2 node list | grep slam
ros2 topic info /map
ros2 topic echo /map --once
```

Sau khi quét map xong:

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/office
```

Full mission với map vừa lưu:

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=$HOME/maps/office.yaml \
  use_sim_time:=true \
  use_rviz:=true
```
