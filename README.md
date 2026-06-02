# 🤖 Edge-Optimized Vision-Guided Navigation for TurtleBot 4 Lite

> Điều hướng robot di động dựa trên thị giác với mô hình AI tối ưu hóa cho thiết bị biên trên TurtleBot 4 Lite

## 📖 1. Tổng quan dự án

Dự án xây dựng hệ thống điều hướng robot di động dựa trên thị giác cho **TurtleBot 4 Lite**. Robot tuần tra trong bản đồ đã biết bằng **ROS 2 Navigation2 (Nav2)**, sử dụng camera **OAK-D-Lite RGB-D** để phát hiện vật thể mục tiêu bằng mô hình object detection nhẹ. Khi phát hiện vật thể, hệ thống ước lượng vị trí 3D, chuyển sang tọa độ bản đồ, sinh goal an toàn và gửi cho Nav2 để tiếp cận mục tiêu.

**Stack công nghệ:** ROS 2 Humble · Python · OpenCV DNN · MobileNet-SSD · Nav2 · Gazebo · OAK-D-Lite

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
| `tb4_vision_oak` | Nhận diện vật thể bằng OAK-D + MobileNet-SSD | ✅ Hoàn thành |
| `tb4_object_localization` | Định vị 3D vật thể từ depth + broadcast TF | ✅ Hoàn thành |
| `tb4_nav_patrol` | Tuần tra tự động bằng Nav2 Action Client | ✅ Hoàn thành |
| `tb4_mission_manager` | Quản lý nhiệm vụ & sinh goal tiếp cận an toàn | ✅ Hoàn thành |
| `tb4_bringup` | Launch file tổng hợp Nav2 + RViz2 + toàn bộ modules | ✅ Hoàn thành |

---

## 🚀 4. Cài đặt & Sử dụng

### Yêu cầu hệ thống

- **OS:** Ubuntu 22.04
- **ROS 2:** Humble Hawksbill
- **Phần mềm bổ sung:** Gazebo, Nav2, SLAM Toolbox, OpenCV, cv_bridge, tf2_ros

### Clone & Build

```bash
git clone https://github.com/<owner>/Robots_Sensor_Actuators.git
cd Robots_Sensor_Actuators

# Tạo workspace (nếu chưa có)
mkdir -p ~/tb4_project_ab/src
ln -s $(pwd) ~/tb4_project_ab/src/Robot-s-Sensor-Actuators-

# Build
cd ~/tb4_project_ab
colcon build --symlink-install
source install/setup.bash
```

### Quy trình vận hành (Workflow)

Hệ thống hoạt động qua **2 giai đoạn chính**:

#### 🔹 Giai đoạn 1: Tạo bản đồ (SLAM Mapping)

> **Mục đích:** Robot tự di chuyển và quét môi trường để tạo file bản đồ (.yaml + .pgm)

1. **Khởi động Gazebo + SLAM:**
   ```bash
   ros2 launch tb4_bringup slam_demo.launch.py
   ```

2. **Di chuyển robot để quét bản đồ:**
   - **Cách 1:** Dùng nút `2D Goal Pose` trong RViz2 để robot tự di chuyển
   - **Cách 2:** Dùng lệnh Teleop (điều khiển thủ công):
     ```bash
     ros2 run teleop_twist_keyboard teleop_twist_keyboard
     ```

3. **Lưu bản đồ khi đã quét xong:**
   ```bash
   # Tạo thư mục maps (nếu chưa có)
   mkdir -p ~/tb4_project_ab/src/Robots_Sensor_Actuators/tb4_bringup/maps

   # Lưu bản đồ
   ros2 run nav2_map_server map_saver_cli \
     -f ~/tb4_project_ab/src/Robots_Sensor_Actuators/tb4_bringup/maps/office
   ```
   → Sẽ tạo ra 2 file: `office.yaml` và `office.pgm`

#### 🔹 Giai đoạn 2: Điều hướng & Nhận diện (Navigation & Detection)

> **Mục đích:** Robot sử dụng bản đồ đã tạo để tuần tra, nhận diện vật thể và tiếp cận mục tiêu

1. **Chạy toàn bộ hệ thống:**
   ```bash
   ros2 launch tb4_bringup sim_demo.launch.py
   ```

2. **Hoặc chạy từng module riêng lẻ:**
   ```bash
   ros2 launch tb4_vision_oak oak_detection.launch.py
   ros2 launch tb4_object_localization localization.launch.py
   ros2 launch tb4_nav_patrol nav_patrol.launch.py
   ros2 launch tb4_mission_manager mission_manager.launch.py
   ```

### Chạy trên robot thật

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py
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
│   ├── config/camera_params.yaml      # Cấu hình ngưỡng AI, FPS
│   ├── launch/oak_detection.launch.py
│   ├── models/                        # MobileNet-SSD (.prototxt, .caffemodel, .blob)
│   ├── scripts/detection_node.py      # Node nhận diện vật thể
│   └── setup.py
├── tb4_object_localization/           # Module định vị 3D
│   ├── launch/localization.launch.py
│   ├── scripts/localization_node.py   # Node tính tọa độ 3D & broadcast TF
│   ├── CMakeLists.txt
│   └── package.xml
├── tb4_nav_patrol/                    # Module tuần tra Nav2
│   ├── launch/nav_patrol.launch.py
│   ├── scripts/patrol_node.py         # Nav2 Action Client, waypoint navigation
│   └── README.md
├── tb4_mission_manager/               # Module quản lý nhiệm vụ
│   ├── launch/mission_manager.launch.py
│   ├── scripts/mission_manager_node.py # Logic sinh safe goal
│   └── README.md
└── tb4_bringup/                       # Launch tổng hợp
    ├── launch/
    │   ├── slam_demo.launch.py        # Launch SLAM mapping
    │   ├── sim_demo.launch.py         # Launch Navigation mô phỏng
    │   └── real_robot_demo.launch.py  # Launch robot thật
    ├── maps/                          # Thư mục chứa bản đồ (.yaml + .pgm)
    └── README.md
```

---

## 📡 6. ROS 2 Topics & TF

| Topic | Producer | Consumer | Msg Type |
|-------|----------|----------|----------|
| `/oakd/rgb/preview/image_raw` | OAK-D | tb4_vision_oak | sensor_msgs/Image |
| `/oakd/rgb/preview/depth` | OAK-D | tb4_object_localization | sensor_msgs/Image |
| `/oakd/rgb/preview/camera_info` | OAK-D | tb4_object_localization | sensor_msgs/CameraInfo |
| `/vision/detected_objects` | tb4_vision_oak | tb4_mission_manager | vision_msgs/Detection2DArray |
| `/target_object_pose_map` | tb4_object_localization | tb4_mission_manager | geometry_msgs/PoseStamped |
| `/goal_pose` | tb4_mission_manager | Nav2 | geometry_msgs/PoseStamped |
| `/navigate_to_pose` | Nav2 | tb4_nav_patrol | nav2_msgs/NavigateToPose |

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
- [OpenCV DNN Module](https://docs.opencv.org/4.x/d2/d58/tutorial_table_of_content_dnn.html)
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
