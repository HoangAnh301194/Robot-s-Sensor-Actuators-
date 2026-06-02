# 📦 tb4_bringup (System Bringup)

## 📖 1. Tổng quan (Overview)

`tb4_bringup` là package tổng hợp, chịu trách nhiệm khởi động toàn bộ hệ thống robot. Package cung cấp các launch file orchestration để chạy đồng thời tất cả các module:

- Nav2 + Patrol (`tb4_nav_patrol`)
- OAK-D Detection (`tb4_vision_oak`)
- 3D Object Localization (`tb4_object_localization`)
- Mission Manager (`tb4_mission_manager`)
- RViz2 để quan sát và set 2D Pose Estimate ban đầu

---

## 🚀 2. Cách sử dụng

### Mô phỏng (Simulation)

```bash
# Source workspace
cd ~/tb4_project_ab
source install/setup.bash

# Launch toàn bộ hệ thống mô phỏng
ros2 launch tb4_bringup sim_demo.launch.py
```

### Robot thật

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py
```

---

## 📂 3. Cấu trúc thư mục

```
tb4_bringup/
├── launch/
│   ├── sim_demo.launch.py            # Launch toàn bộ hệ thống trên mô phỏng
│   └── real_robot_demo.launch.py     # Launch toàn bộ hệ thống trên robot thật
├── config/                            # Cấu hình tham số chung
├── maps/                              # Bản đồ mô phỏng (office.yaml)
└── README.md                          # Tài liệu này
```

---

## 📋 4. Launch File chi tiết

### `sim_demo.launch.py`

Launch file tổng hợp cho mô phỏng, bao gồm:

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
