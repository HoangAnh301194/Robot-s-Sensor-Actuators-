# 📦 tb4_bringup (System Bringup)

## 📖 1. Tổng quan (Overview)

`tb4_bringup` là package tổng hợp, chịu trách nhiệm khởi động toàn bộ hệ thống robot. Package cung cấp các launch file orchestration để chạy đồng thời tất cả các module.

---

## 🚀 2. Quy trình vận hành

### Bước 1: Tạo bản đồ (SLAM)

```bash
ros2 launch tb4_bringup slam_demo.launch.py
```

**Thao tác trong RViz2:**
- Dùng nút `2D Goal Pose` để robot tự di chuyển và quét bản đồ
- Quan sát bản đồ được xây dựng trong thời gian thực

**Lưu bản đồ:**
```bash
mkdir -p ~/tb4_project_ab/src/Robots_Sensor_Actuators/tb4_bringup/maps

ros2 run nav2_map_server map_saver_cli \
  -f ~/tb4_project_ab/src/Robots_Sensor_Actuators/tb4_bringup/maps/office
```

→ Tạo ra 2 file: `office.yaml` + `office.pgm`

---

### Bước 2: Điều hướng & Nhận diện

```bash
ros2 launch tb4_bringup sim_demo.launch.py
```

Hoặc chỉ định bản đồ tùy chỉnh:
```bash
ros2 launch tb4_bringup sim_demo.launch.py map:=/path/to/your/map.yaml
```

---

### Bước 3 (Tùy chọn): Robot thật

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py
```

---

## 📂 3. Cấu trúc thư mục

```
tb4_bringup/
├── launch/
│   ├── slam_demo.launch.py            # Launch SLAM mapping
│   ├── sim_demo.launch.py             # Launch Navigation mô phỏng
│   └── real_robot_demo.launch.py      # Launch robot thật
├── maps/                               # Bản đồ (.yaml + .pgm) sau khi SLAM
│   ├── office.yaml                     # Metadata bản đồ
│   └── office.pgm                      # Ảnh bản đồ grayscale
├── config/                             # Cấu hình Nav2 params
├── package.xml
├── setup.py
└── README.md                           # Tài liệu này
```

---

## 📋 4. Launch File chi tiết

### `slam_demo.launch.py`

Launch file cho giai đoạn SLAM mapping:

1. **SLAM Toolbox** (`slam_toolbox/online_async_launch.py`) — Tạo bản đồ từ Lidar
2. **OAK-D Detection** (`tb4_vision_oak/oak_detection.launch.py`) — Nhận diện vật thể
3. **Object Localization** (`tb4_object_localization/localization.launch.py`) — Định vị 3D
4. **RViz2** — Hiển thị bản đồ + TF

### `sim_demo.launch.py`

Launch file cho giai đoạn Navigation:

1. **Nav2 Launch** (`nav2_bringup/bringup_launch.py`) — Navigation + Localization
2. **Nav Patrol** (`tb4_nav_patrol/nav_patrol.launch.py`) — Tuần tra tự động
3. **OAK-D Detection** (`tb4_vision_oak/oak_detection.launch.py`) — Nhận diện vật thể
4. **Object Localization** (`tb4_object_localization/localization.launch.py`) — Định vị 3D
5. **Mission Manager** (`tb4_mission_manager/mission_manager.launch.py`) — Quản lý nhiệm vụ
6. **RViz2** — Hiển thị trực quan

---

## 🔨 5. Build

```bash
colcon build --packages-select tb4_bringup
source install/setup.bash
```
