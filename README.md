# 🤖 Edge-Optimized Vision-Guided Navigation for TurtleBot 4 Lite

> Điều hướng robot di động dựa trên thị giác với mô hình AI tối ưu hóa cho thiết bị biên trên TurtleBot 4 Lite

## 📖 1. Tổng quan dự án

Dự án xây dựng hệ thống điều hướng robot di động dựa trên thị giác cho **TurtleBot 4 Lite**. Robot tuần tra trong bản đồ đã biết bằng **ROS 2 Navigation2 (Nav2)**, sử dụng camera **OAK-D-Lite RGB-D** để phát hiện vật thể mục tiêu bằng mô hình object detection nhẹ. Khi phát hiện vật thể, hệ thống ước lượng vị trí 3D, chuyển sang tọa độ bản đồ, sinh goal an toàn và gửi cho Nav2 để tiếp cận mục tiêu.

**Stack công nghệ:** ROS 2 Humble · Python · Ultralytics YOLOv8n · OpenCV · Nav2 · Gazebo · OAK-D-Lite

---

## 🏗️ 2. Kiến trúc hệ thống

```
                    ┌──────────────────┐
                    │  TurtleBot 4 Lite │
                    │ (base, odometry)  │
                    └───────┬──────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
       ┌────▼────┐   ┌─────▼─────┐   ┌─────▼─────┐
       │   Nav2  │   │ OAK-D Lite│   │ Base Link │
       │         │   │   RGB-D   │   │    TF     │
       └────┬────┘   └─────┬─────┘   └─────┬─────┘
            │               │               │
            │               ▼               │
            │        ┌──────────────┐       │
            │        │ tb4_vision   │       │
            │        │    _oak      │       │
            │        │ (detection)  │       │
            │        └──────┬───────┘       │
            │               │               │
            │               ▼               │
            │        ┌───────────────┐      │
            │        │tb4_object_loc │      │
            │        │  alization    │      │
            │        │ (3D pose, TF) │      │
            │        └──────┬────────┘      │
            │               │               │
            │               ▼               │
            │        ┌───────────────┐      │
            │        │tb4_mission_   │      │
            │        │  manager      │      │
            │        │(goal gen)     │      │
            │        └──────┬────────┘      │
            │               │               │
            └───────────────┼───────────────┘
                            │
                    ┌───────▼──────────┐
                    │  tb4_bringup     │
                    │ (orchestration)  │
                    └──────────────────┘
```

### Luồng dữ liệu

1. **Cảm biến**: Robot cung cấp odometry, TF tree
2. **Vision**: OAK-D camera → detection (bounding boxes)
3. **Localization**: depth + detection → 3D object pose + TF
4. **Mission**: object pose → safe goal → Nav2
5. **Navigation**: Nav2 lập kế hoạch & điều khiển robot

---

## 📦 3. Các Package

| Package | Mô tả | Trạng thái |
|---------|-------|------------|
| `tb4_vision_oak` | Nhận diện vật thể bằng OAK-D + YOLOv8n | ✅ Hoàn thành |
| `tb4_object_localization` | Định vị 3D vật thể từ depth + broadcast TF | ✅ Hoàn thành |
| `tb4_nav_patrol` | Tuần tra tự động bằng Nav2 Action Client | ✅ Hoàn thành |
| `tb4_mission_manager` | Quản lý nhiệm vụ & sinh goal tiếp cận an toàn | ✅ Hoàn thành |
| `tb4_bringup` | Launch file tổng hợp Nav2 + RViz2 + toàn bộ modules | ✅ Hoàn thành |

---

## 🚀 4. Cài đặt & Sử dụng

### Yêu cầu hệ thống

- **OS:** Ubuntu 22.04
- **ROS 2:** Humble Hawksbill
- **Các package chính:** `turtlebot4_navigation`, `nav2_bringup`, `slam_toolbox`, `rviz2`

### Clone & Build

```bash
git clone https://github.com/<owner>/Robots_Sensor_Actuators.git
cd Robots_Sensor_Actuators

mkdir -p ~/tb4_project_ab/src
ln -s "$(pwd)" ~/tb4_project_ab/src/Robots_Sensor_Actuators

cd ~/tb4_project_ab
PYTHONNOUSERSITE=1 colcon build --symlink-install
source install/setup.bash
```

> Nếu trong repo có thư mục `venv`, tạo file `venv/COLCON_IGNORE` để `colcon` không nhận nhầm package Python trong virtualenv.

### Chuẩn môi trường cho mọi terminal

Dự án này nên chạy cùng một ROS domain để tránh lẫn graph với các phiên ROS/Gazebo cũ. Mỗi terminal mới đều chạy:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash
```

Kiểm tra overlay `turtlebot4_description` đang được dùng. Overlay này nâng vị trí RPLIDAR trong mô phỏng TurtleBot4 Lite để tránh lỗi `/scan` toàn `0.164`:

```bash
ros2 pkg prefix turtlebot4_description
```

Kỳ vọng:

```text
/home/hoang_anh/tb4_project_ab/install/turtlebot4_description
```

### Điều kiện trước khi chạy

`tb4_bringup` orchestration phần Nav2 + perception + mission logic, nhưng **không tự spawn robot simulator hoặc camera publisher**. Trước khi chạy full stack cần có sẵn:

- `/clock`, `/tf`, `/odom`, `/scan`
- `/oakd/rgb/preview/image_raw`
- `/oakd/rgb/preview/depth`
- `/oakd/rgb/preview/camera_info`

Các topic này đến từ simulator chính thức `turtlebot4_ignition_bringup`.

### Dọn sạch simulator cũ

Gazebo/Ignition transport không tách hoàn toàn theo `ROS_DOMAIN_ID`. Nếu còn `ruby ign gazebo`, `parameter_bridge`, launch cũ, hoặc FastDDS shared-memory lock cũ bị treo, ROS có thể nhìn thấy topic đúng tên nhưng dữ liệu đến từ world/session cũ. Triệu chứng thường gặp là `/scan` vẫn có rate nhưng toàn `0.164`, `/clock` không nhảy, robot không spawn đúng, hoặc controller chờ mãi.

#### Dọn nhanh trước mỗi lần launch simulator

Chạy lệnh này trước khi mở lại simulator:

```bash
killall -9 ruby parameter_bridge robot_state_publisher joint_state_publisher spawner turtlebot4_node \
  hazards_vector_publisher ir_intensity_vector_publisher motion_control wheel_status_publisher \
  mock_publisher robot_state kidnap_estimator_publisher ui_mgr pose_republisher_node sensors_node \
  interface_buttons_node static_transform_publisher create 2>/dev/null || true
```

Nếu trước đó có nhiều terminal `ros2 launch` bị treo, kiểm tra và tự đóng/`Ctrl+C` terminal đó. Nếu cần dọn mạnh cả tiến trình launch ROS 2 cũ, dùng thêm:

```bash
pkill -9 -f "ros2 launch turtlebot4_ignition_bringup" 2>/dev/null || true
pkill -9 -f "ros2 launch tb4_bringup" 2>/dev/null || true
```

#### Xóa cache/log/session tạm khi bị lỗi lặp lại

Các lệnh dưới đây chỉ xóa file tạm/log/lock, không xóa source code hay package đã build:

```bash
rm -f /tmp/launch_params_* 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
rm -rf ~/.ros/log/* 2>/dev/null || true
rm -rf ~/.ignition/gazebo/log/* ~/.gz/sim/log/* 2>/dev/null || true
```

Không nên xóa `~/.ignition/fuel` hoặc `~/.gz/fuel` trừ khi muốn tải lại toàn bộ model/world từ đầu.

#### Kiểm tra còn server/session cũ không

Sau khi dọn, kiểm tra:

```bash
ps -eo pid,comm,args | grep -E "ign gazebo|ruby|parameter_bridge|turtlebot4_ignition|robot_state_publisher" | grep -v grep
```

Nếu lệnh trên không in ra gì, môi trường đã sạch. Sau đó mở terminal mới và source lại môi trường như phần trên.

### Launch simulator TurtleBot4 Lite

Terminal 1:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  model:=lite \
  world:=warehouse \
  x:=2.0 y:=0.0 z:=0.01 yaw:=0.0
```

Đợi đến khi thấy controller active:

```text
Configured and activated joint_state_broadcaster
Configured and activated diffdrive_controller
```

Kiểm tra simulator có dữ liệu thật ở terminal khác:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 topic echo /clock --once
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 topic echo /oakd/rgb/preview/camera_info --once
```

`/scan` đúng sẽ có nhiều giá trị khác nhau, ví dụ `inf`, `4.x`, `6.x`, `11.x`. Nếu `/scan` toàn `0.164`, dọn sạch simulator cũ rồi launch lại từ terminal mới.

### Test từng module và visualization/debug

Giữ terminal simulator đang chạy, sau đó test từng module theo thứ tự sau.

#### 1) Vision Detection

Terminal 2:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch tb4_vision_oak oak_detection.launch.py show_debug_window:=false
```

Module luôn dùng mặc định `yolov8n.pt`. Nếu `tb4_vision_oak/models/yolov8n.pt` tồn tại thì node dùng file local; nếu chưa có, Ultralytics sẽ tự download lần đầu chạy.

Kiểm tra output:

```bash
ros2 topic list | grep vision
ros2 topic hz /vision/detected_objects
ros2 topic echo /vision/detected_objects --once
```

Debug ảnh trong RViz bằng topic:

```text
/vision/debug_image
```

Nếu muốn thử cửa sổ OpenCV trực tiếp:

```bash
ros2 launch tb4_vision_oak oak_detection.launch.py show_debug_window:=true
```

Nếu OpenCV báo `cvShowImage`/HighGUI chưa được build với GTK/Qt, dùng `show_debug_window:=false` và xem camera bằng RViz `Image`.

#### 2) Object Localization

Terminal 3:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch tb4_object_localization localization.launch.py
```

Kiểm tra input camera/depth và output pose/marker:

```bash
ros2 topic hz /oakd/rgb/preview/image_raw
ros2 topic hz /oakd/rgb/preview/depth
ros2 topic echo /oakd/rgb/preview/camera_info --once
ros2 topic list | grep target
ros2 topic echo /target_object_pose_map --once
ros2 topic echo /target_object_marker --once
```

`/target_object_pose_map` và `/target_object_marker` chỉ có dữ liệu khi YOLO detect được người/vật thể và depth hợp lệ. Với YOLOv8n, node localization ưu tiên class `person` (`class_id=0`) rồi publish chấm tròn marker màu đỏ/cam để xem trong RViz.

#### 3) RViz debug dashboard

Terminal 4:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

rviz2 -d ~/tb4_project_ab/install/tb4_bringup/share/tb4_bringup/rviz/tb4_debug.rviz
```

Dashboard đã có sẵn:

- `Map`: topic `/map`
- `LaserScan`: topic `/scan`
- `TF`: xem cây frame robot/camera/object
- `Image`: topic `/oakd/rgb/preview/image_raw`
- `Image`: topic `/vision/debug_image` để xem ảnh đã vẽ bounding box detection
- `Pose`: topic `/target_object_pose_map`
- `Marker`: topic `/target_object_marker` để xem chấm tròn vị trí người/vật thể
- `Path`: topic `/plan` để debug Nav2

Lưu ý:

- Nếu chỉ chạy detection + localization mà chưa có `map -> odom -> base_link -> oakd_link`, đổi `Global Options > Fixed Frame` sang `oakd_link` để thấy marker.
- Khi chạy Nav2/SLAM đầy đủ, đổi `Fixed Frame` về `map`.
- Warning `No map received` là bình thường nếu chưa chạy SLAM hoặc Nav2 localization với map có sẵn.

#### 4) Nav2 + Patrol + Mission Manager

Chỉ chạy phần này khi simulator đã có `/scan`, `/odom`, `/tf`, `/clock`.

Kiểm tra Nav2 action server sau khi launch:

```bash
ros2 action list | grep navigate
```

Kỳ vọng có:

```text
/navigate_to_pose
```

### Workflow full chức năng dự án

Có 2 chế độ chạy full: dùng map có sẵn hoặc tự SLAM tạo map.

#### Chế độ A: Full mission với map có sẵn

Terminal 1 chạy simulator như phần trên. Sau khi `/scan` đúng, mở terminal 2 chạy toàn bộ stack:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch tb4_bringup sim_demo.launch.py   map:=/opt/ros/humble/share/turtlebot4_navigation/maps/warehouse.yaml   use_sim_time:=true   use_rviz:=true   show_debug_window:=false
```

Launch này khởi động:

- Nav2 localization
- Nav2 navigation server
- Patrol node
- YOLOv8n detection
- Object localization 3D
- Mission Manager
- RViz dashboard nếu `use_rviz:=true`

Luồng full tính năng:

```text
Simulator/OAK-D/RPLIDAR
→ YOLOv8n detect người/vật thể
→ Object localization tính pose 3D + marker
→ Mission Manager nhận target pose
→ Mission Manager tạm dừng patrol
→ Mission Manager gửi goal tiếp cận mục tiêu qua Nav2
→ Nav2 điều khiển robot
```

Theo dõi trạng thái:

```bash
ros2 topic echo /target_object_marker --once
ros2 topic echo /target_object_pose_map --once
ros2 topic echo /mission_manager/patrol_enabled
ros2 action list | grep navigate
```

#### Chế độ B: SLAM tạo map rồi chạy full mission

Terminal 1 chạy simulator như phần trên. Terminal 2 chạy SLAM:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch tb4_bringup slam_demo.launch.py use_sim_time:=true use_rviz:=true
```

Điều khiển robot để quét map:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Trong RViz, display `Map /map` sẽ hiện dần vùng đã quét. Nếu chưa thấy map:

```bash
ros2 node list | grep slam
ros2 topic info /map
ros2 topic echo /map --once
```

Lưu map:

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/warehouse_custom --ros-args -p map_subscribe_transient_local:=true
```

Sau đó dừng SLAM, giữ simulator, rồi chạy full mission bằng map vừa lưu:

```bash
ros2 launch tb4_bringup sim_demo.launch.py   map:=~/maps/warehouse_custom.yaml   use_sim_time:=true   use_rviz:=true   show_debug_window:=false
```

### Chạy từng module thủ công

Nếu Nav2 đã chạy sẵn, có thể start riêng các module:

```bash
ros2 launch tb4_vision_oak oak_detection.launch.py
ros2 launch tb4_object_localization localization.launch.py
ros2 launch tb4_nav_patrol nav_patrol.launch.py
ros2 launch tb4_mission_manager mission_manager.launch.py
```

Lưu ý:

- `tb4_nav_patrol` chỉ gửi waypoint tuần tra qua Nav2, không tự bring up Nav2.
- `tb4_mission_manager` nhận target pose, tạm dừng patrol và gửi goal tiếp cận mục tiêu.
- Nếu chỉ test detection/localization, RViz `Fixed Frame` có thể để `oakd_link`.
- Nếu test full navigation/mission, RViz `Fixed Frame` nên để `map`.

### Checklist triển khai end-to-end đã debug

Dùng checklist này khi muốn chạy từ đầu tới cuối ổn định nhất.

#### 1) Reset sạch

```bash
killall -9 ruby parameter_bridge robot_state_publisher joint_state_publisher spawner turtlebot4_node \
  hazards_vector_publisher ir_intensity_vector_publisher motion_control wheel_status_publisher \
  mock_publisher robot_state kidnap_estimator_publisher ui_mgr pose_republisher_node sensors_node \
  interface_buttons_node static_transform_publisher create 2>/dev/null || true
rm -f /tmp/launch_params_* 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
```

#### 2) Launch simulator và xác minh scan/clock

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  model:=lite world:=warehouse x:=2.0 y:=0.0 z:=0.01 yaw:=0.0
```

Terminal kiểm tra:

```bash
ros2 topic echo /clock --once
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

`/scan` đúng phải có nhiều giá trị khác nhau. Nếu toàn `0.164`, đó là world/session cũ hoặc RPLIDAR chưa dùng overlay. Nếu `/clock` không ra dữ liệu, Gazebo server đang stall: dọn sạch và launch lại simulator.

#### 3) Chạy SLAM và tự lái 3 phút

```bash
ros2 launch tb4_bringup slam_demo.launch.py use_sim_time:=true use_rviz:=true show_debug_window:=false
```

`tb4_bringup` dùng cấu hình SLAM riêng tại `tb4_bringup/config/slam_toolbox_tb4.yaml`, trong đó `base_frame: base_link`. Nếu dùng config mặc định của `slam_toolbox`, thường sẽ lỗi `Failed to compute odom pose` vì mặc định là `base_footprint`.

Có thể lái bằng teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Hoặc lái tự động đơn giản để quét map:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.16}, angular: {z: 0.25}}" -r 10
```

Dừng robot:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}" --once
```

#### 4) Lưu map đúng QoS

`/map` của SLAM Toolbox publish kiểu `TRANSIENT_LOCAL`, nên dùng thêm `map_subscribe_transient_local:=true`:

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/tb4_e2e_test \
  --ros-args -p map_subscribe_transient_local:=true
```

Kỳ vọng có:

```text
~/maps/tb4_e2e_test.yaml
~/maps/tb4_e2e_test.pgm
```

#### 5) Restart simulator trước full stack

Sau khi lưu map, dừng SLAM và simulator, dọn process/cache rồi launch simulator lại. Không nên chạy Nav2/full mission ngay trên cùng phiên Gazebo vừa SLAM nếu thấy `/clock` hoặc TF bị đứng.

#### 6) Chạy full stack

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=~/maps/tb4_e2e_test.yaml \
  use_sim_time:=true \
  use_rviz:=true \
  show_debug_window:=false \
  auto_initial_pose:=true \
  initial_pose_x:=0.0 \
  initial_pose_y:=0.0 \
  initial_pose_yaw:=0.0 \
  patrol_start_delay:=45.0
```

`auto_initial_pose:=true` sẽ publish `/initialpose` cho AMCL sau khi Nav2 khởi động. `patrol_start_delay:=45.0` trì hoãn patrol để tránh gửi waypoint trước khi AMCL tạo `map -> odom`.

Kiểm tra full stack:

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 action list | grep navigate
ros2 topic echo /amcl_pose --once
ros2 topic echo /target_object_marker --once
```

Nếu `tf2_echo map odom` chưa có, publish initial pose lại từ RViz bằng nút `2D Pose Estimate`, hoặc chạy lại full stack với `auto_initial_pose:=true` và đúng `initial_pose_x/y/yaw`.

### Troubleshooting nhanh

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|------------|------------------------|------------|
| `/scan` toàn `0.164` | Gazebo server cũ/stale hoặc lidar quét trúng thân robot | Dọn sạch process bằng `killall`, source overlay, launch lại simulator |
| `ros2 pkg prefix turtlebot4_description` ra `/opt/ros/humble` | Chưa source workspace hoặc overlay chưa build | `source ~/tb4_project_ab/install/setup.bash`, build lại `turtlebot4_description` |
| RViz không thấy marker | Fixed Frame không transform được tới `oakd_link` | Đổi Fixed Frame sang `oakd_link` khi test riêng, hoặc chạy full TF/Nav2 rồi dùng `map` |
| `No map received` | Chưa chạy SLAM/localization với map | Chạy `slam_demo.launch.py` hoặc `sim_demo.launch.py` với `map:=...` |
| FastRTPS SHM spam | Shared memory lock cũ | Export `RMW_FASTRTPS_USE_SHM=0` ở mọi terminal |
| Không thấy `/imu` | TurtleBot4 Ignition sim không bridge OAK-D IMU mặc định | Cần tự thêm Gazebo IMU sensor + bridge nếu muốn dùng IMU |

### Checklist debug đã kiểm chứng cho lỗi `/scan`

Nếu chạy đúng mà `/scan` vẫn toàn `0.164` hoặc `1.0`, làm theo checklist này theo đúng thứ tự. Lỗi này thường không phải do SLAM, mà do **simulator/ROS graph cũ**, **RPLIDAR overlay chưa được dùng**, hoặc **ROS_DOMAIN_ID không đồng nhất**.

#### 1) Không đổi `ROS_DOMAIN_ID` giữa chừng

Chọn **một domain duy nhất** cho toàn bộ terminal. Khuyến nghị dùng `7` để tránh lẫn graph với project khác:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash
ros2 daemon stop 2>/dev/null || true
ros2 daemon start
```

Nếu trước đó từng chạy bằng `ROS_DOMAIN_ID=0`, phải dừng toàn bộ process và restart daemon. Không chạy simulator ở domain `0` nhưng kiểm tra topic ở domain `7`, vì khi đó `ros2 topic list` có thể không thấy node/topic thật.

Kiểm tra terminal hiện tại đang ở domain nào:

```bash
echo $ROS_DOMAIN_ID
ros2 daemon status
```

Nếu `.bashrc` có nhiều dòng `export ROS_DOMAIN_ID=0`, hãy sửa lại hoặc luôn export `ROS_DOMAIN_ID=7` ở cuối terminal trước khi launch. Sau khi đổi domain, luôn chạy:

```bash
ros2 daemon stop
ros2 daemon start
```

#### 2) Dọn mạnh toàn bộ session cũ

Khi simulator bị treo, `killall` thường chưa đủ vì còn `ign gazebo server/gui`, `ros2 launch`, hoặc `python3` node con. Dùng khối lệnh này trước khi test lại:

```bash
killall -9 ruby ign create parameter_bridge robot_state_publisher joint_state_publisher spawner \
  turtlebot4_node hazards_vector_publisher ir_intensity_vector_publisher motion_control \
  wheel_status_publisher mock_publisher robot_state kidnap_estimator_publisher ui_mgr \
  pose_republisher_node sensors_node interface_buttons_node static_transform_publisher \
  rviz2 async_slam_toolbox_node 2>/dev/null || true

pkill -9 -f "ros2 launch turtlebot4_ignition_bringup" 2>/dev/null || true
pkill -9 -f "ros2 launch tb4_bringup" 2>/dev/null || true
pkill -9 -f "ign gazebo" 2>/dev/null || true
pkill -9 -f "parameter_bridge" 2>/dev/null || true

rm -f /tmp/launch_params_* 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true

ros2 daemon stop 2>/dev/null || true
```

Sau đó mở terminal mới hoặc source lại môi trường:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash
ros2 daemon start
```

#### 3) Kiểm tra overlay RPLIDAR đang được dùng

```bash
ros2 pkg prefix turtlebot4_description
```

Kỳ vọng phải là workspace overlay:

```text
/home/hoang_anh/tb4_project_ab/install/turtlebot4_description
```

Nếu ra `/opt/ros/humble`, build và source lại:

```bash
cd ~/tb4_project_ab
PYTHONNOUSERSITE=1 colcon build --symlink-install \
  --packages-select turtlebot4_description \
  --allow-overriding turtlebot4_description
source install/setup.bash
```

Kiểm tra URDF đã nâng lidar lên cao chưa:

```bash
ros2 run xacro xacro \
  ~/tb4_project_ab/src/turtlebot4_description/urdf/lite/turtlebot4.urdf.xacro \
  gazebo:=ignition | grep rplidar_joint -A 5
```

Kỳ vọng `xyz` của `rplidar_joint` có `z` khoảng `0.2642`, không phải khoảng `0.139`.

#### Lỗi diffdrive_controller inactive / Switch controller timed out

Nếu thấy log:

```text
[ERROR] Switch controller timed out after 5.000000 seconds!
[ERROR] Failed to activate controller : diffdrive_controller
```

Nguyên nhân: Gazebo physics chạy chậm (do máy nặng, load world lâu, GUI rendering), trong khi spawner mặc định chỉ đợi **5 giây** để switch controller.

Cách sửa: workspace overlay `irobot_create_control` đã được tạo tại `~/tb4_project_ab/src/irobot_create_control/` với 2 thay đổi:

1. `config/control.yaml`: giảm `update_rate` từ `1000` xuống `50` Hz
2. `launch/include/control.py`: thêm `--controller-manager-timeout 60 --switch-timeout 30` cho spawner

Build lại overlay nếu chưa có:

```bash
cd ~/tb4_project_ab
PYTHONNOUSERSITE=1 colcon build --symlink-install \
  --packages-select irobot_create_control \
  --allow-overriding irobot_create_control
source install/setup.bash
```

Kiểm tra overlay đúng:

```bash
ros2 pkg prefix irobot_create_control
```

Kỳ vọng:

```text
/home/hoang_anh/tb4_project_ab/install/irobot_create_control
```

Nếu overlay đúng mà vẫn timeout, kiểm tra `/clock` có nhảy không (nếu `sec: 0` không tăng, Gazebo bị đứng — cần đợi GUI render xong hoặc click Play trong Gazebo).

#### 4) Launch simulator rồi đợi đủ lâu

```bash
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  model:=lite world:=warehouse x:=2.0 y:=0.0 z:=0.01 yaw:=0.0
```

Đợi ít nhất 20-30 giây, tới khi robot spawn xong và controller active. Nếu thấy `Waiting messages on topic [robot_description]` quá lâu, chưa nên chạy SLAM/Nav2.

Terminal kiểm tra:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash
ros2 daemon stop
ros2 daemon start

ros2 node list | grep lidar
ros2 topic echo /clock --once
ros2 topic echo /scan --once
ros2 topic echo /odom --once
```

`/scan` đúng sẽ có nhiều giá trị khác nhau, ví dụ:

```text
- .inf
- 11.7
- 9.9
- 6.3
- 5.0
```

Nếu `/scan` chỉ toàn `0.164`, nguyên nhân gần như chắc chắn là world/session cũ hoặc overlay chưa được dùng. Quay lại bước dọn mạnh.

#### 5) Điều kiện tối thiểu trước khi chạy SLAM

Chỉ chạy `slam_demo.launch.py` khi các lệnh này đều có dữ liệu:

```bash
ros2 topic hz /clock
ros2 topic hz /scan
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

Nếu `/scan` có dữ liệu nhưng `tf2_echo odom base_link` không có transform, SLAM sẽ không tạo `/map`. Khi đó cần kiểm tra controller/diffdrive trong log simulator, không debug ở `slam_toolbox` trước.

### Quy trình end-to-end khuyến nghị

Quy trình ổn định nhất là tách thành 2 phiên: **phiên SLAM để tạo map**, sau đó **restart simulator** và chạy full mission với map vừa lưu.

#### Phiên A: quét map SLAM trong 3 phút

Terminal 1: dọn sạch và launch simulator.

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  model:=lite world:=warehouse x:=2.0 y:=0.0 z:=0.01 yaw:=0.0
```

Terminal 2: chạy SLAM + RViz.

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch tb4_bringup slam_demo.launch.py \
  use_sim_time:=true \
  use_rviz:=true \
  show_debug_window:=false
```

Terminal 3: lái robot tự do trong khoảng 3 phút.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Nếu muốn tự động quay/chạy chậm để test nhanh:

```bash
timeout 180s ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.16}, angular: {z: 0.25}}" -r 10

ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}" --once
```

Lưu map:

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/tb4_e2e_test \
  --ros-args -p map_subscribe_transient_local:=true
```

Kiểm tra file:

```bash
ls -lh ~/maps/tb4_e2e_test.yaml ~/maps/tb4_e2e_test.pgm
```

#### Phiên B: chạy full mission trên map đã lưu

Dừng toàn bộ phiên SLAM/simulator bằng `Ctrl+C`, sau đó dọn mạnh bằng khối cleanup ở trên. Launch simulator lại từ đầu.

Terminal 1:

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  model:=lite world:=warehouse x:=2.0 y:=0.0 z:=0.01 yaw:=0.0
```

Terminal 2: chạy toàn bộ stack.

```bash
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source ~/tb4_project_ab/install/setup.bash

ros2 launch tb4_bringup sim_demo.launch.py \
  map:=~/maps/tb4_e2e_test.yaml \
  use_sim_time:=true \
  use_rviz:=true \
  show_debug_window:=false \
  auto_initial_pose:=true \
  initial_pose_x:=0.0 \
  initial_pose_y:=0.0 \
  initial_pose_yaw:=0.0 \
  patrol_start_delay:=45.0
```

Kiểm tra full stack:

```bash
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 action list | grep navigate
ros2 topic echo /vision/detected_objects --once
ros2 topic echo /target_object_marker --once
```

Trong RViz nên bật các display:

- `Map`: `/map`
- `LaserScan`: `/scan`
- `TF`: kiểm tra `map -> odom -> base_link -> oakd_link`
- `Image`: `/vision/debug_image` hoặc `/oakd/rgb/preview/image_raw`
- `Marker`: `/target_object_marker`
- `MarkerArray`: `/target_object_marker_array`
- `Pose`: `/target_object_pose_map`
- `Path`: `/plan`, `/local_plan` nếu cần debug Nav2

### Chạy trên robot thật

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py \
  map:=~/maps/office.yaml \
  use_rviz:=true
```

---

## 🔧 5. Cấu trúc thư mục

```
Robots_Sensor_Actuators/
├── README.md                          # Tài liệu chính
├── docs/
│   └── ARCHITECTURE.md                # Kiến trúc chi tiết
├── GitHub_turtorial.md                # Hướng dẫn Git workflow
├── tb4_vision_oak/                    # Module nhận diện OAK-D
│   ├── config/camera_params.yaml      # Cấu hình detection
│   ├── launch/oak_detection.launch.py
│   ├── models/                        # yolov8n.pt local tùy chọn
│   ├── tb4_vision_oak/detection_node.py
│   ├── scripts/detection_node.py      # Wrapper tương thích
│   └── setup.py
├── tb4_object_localization/           # Module định vị 3D
│   ├── launch/localization.launch.py
│   ├── scripts/localization_node.py   # Node tính tọa độ 3D & broadcast TF
│   ├── CMakeLists.txt
│   └── package.xml
├── tb4_nav_patrol/                    # Module tuần tra Nav2
│   ├── launch/nav_patrol.launch.py
│   ├── tb4_nav_patrol/patrol_node.py
│   ├── scripts/patrol_node.py         # Wrapper tương thích
│   └── README.md
├── tb4_mission_manager/               # Module quản lý nhiệm vụ
│   ├── launch/mission_manager.launch.py
│   ├── tb4_mission_manager/mission_manager_node.py
│   ├── scripts/mission_manager_node.py # Wrapper tương thích
│   └── README.md
├── turtlebot4_description/            # Overlay mô phỏng: nâng RPLIDAR Lite để fix /scan 0.164
│   ├── launch/robot_description.launch.py
│   ├── urdf/lite/turtlebot4.urdf.xacro
│   └── CMakeLists.txt
└── tb4_bringup/                       # Launch tổng hợp
    ├── launch/
    │   ├── slam_demo.launch.py
    │   ├── sim_demo.launch.py
    │   └── real_robot_demo.launch.py
    ├── tb4_bringup/launch_utils.py    # Helper chọn map/params mặc định
    └── README.md
```

---

## 📡 6. ROS 2 Topics & TF

| Topic | Producer | Consumer | Msg Type |
|-------|----------|----------|----------|
| `/oakd/rgb/preview/image_raw` | OAK-D | tb4_vision_oak | sensor_msgs/Image |
| `/oakd/rgb/preview/depth` | OAK-D | tb4_object_localization | sensor_msgs/Image |
| `/oakd/rgb/preview/camera_info` | OAK-D | tb4_object_localization | sensor_msgs/CameraInfo |
| `/vision/detected_objects` | tb4_vision_oak | tb4_object_localization | vision_msgs/Detection2DArray |
| `/target_object_pose_map` | tb4_object_localization | tb4_mission_manager | geometry_msgs/PoseStamped |
| `/mission_manager/patrol_enabled` | tb4_mission_manager | tb4_nav_patrol | std_msgs/Bool |

### ROS 2 Actions

| Action | Client |
|--------|--------|
| `navigate_to_pose` | `tb4_nav_patrol`, `tb4_mission_manager` |

### Cấu trúc TF

```
map
 └── odom
      └── base_footprint
           └── base_link
                ├── camera_link
                │   └── camera_optical_frame
                ├── oakd_link
                │   └── detected_object_3d   ← (TF động từ localization node)
                └── caster_wheel_link
```

---

## 📚 7. Tài liệu tham khảo

- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)
- [Nav2 Documentation](https://docs.nav2.org/)
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [TurtleBot 4 User Manual](https://turtlebot.github.io/turtlebot4-user-manual/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [Luxonis OAK-D](https://docs.luxonis.com/)

---

## 👥 8. Thành viên & Phân công

| Thành viên | Module | Branch |
|------------|--------|--------|
| Member 1 | Nav2 patrol & simulation | `feature/nav2-patrol` |
| Member 2 | OAK-D detection | `feature/oakd-detection` |
| Member 3 | Object localization | `feature/object-localization` |
| Member 4 | Mission manager | `feature/mission-manager` |

---

## 📄 License

Apache-2.0
