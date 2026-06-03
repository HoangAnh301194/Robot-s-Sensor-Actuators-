# 📦 tb4_bringup (System Bringup)

## Tổng quan

`tb4_bringup` là package orchestration của project. Package này chịu trách nhiệm ghép:

- `turtlebot4_navigation` cho localization + Nav2
- `tb4_nav_patrol` cho waypoint patrol
- `tb4_vision_oak` cho object detection
- `tb4_object_localization` cho 3D localization
- `tb4_mission_manager` cho goal takeover khi phát hiện mục tiêu

Lưu ý: package này **không tự spawn simulator hoặc camera publisher**. Trước khi chạy, hệ thống cần sẵn các topic nền như `/tf`, `/scan`, `/oakd/rgb/preview/image_raw`, `/oakd/rgb/preview/depth`.

## Các Launch chính

### `slam_demo.launch.py`

Chạy SLAM Toolbox cùng perception stack:

```bash
ros2 launch tb4_bringup slam_demo.launch.py use_sim_time:=true use_rviz:=true
```

Tùy chọn:

- `use_rviz:=true|false`
- `show_debug_window:=true|false`

### `sim_demo.launch.py`

Chạy full application stack cho mô phỏng hoặc laptop test:

```bash
ros2 launch tb4_bringup sim_demo.launch.py \
  map:=/path/to/map.yaml \
  use_sim_time:=true \
  use_rviz:=true
```

Nếu không truyền `map:=...`, launch sẽ dùng map mẫu mặc định từ `turtlebot4_navigation` nếu package đó có sẵn.

Tham số:

- `map`: file `.yaml` của occupancy map
- `params_file`: file config Nav2, mặc định lấy từ `turtlebot4_navigation/config/nav2.yaml`
- `use_rviz`: bật/tắt RViz
- `show_debug_window`: bật/tắt cửa sổ OpenCV detection

### `real_robot_demo.launch.py`

Chạy stack tương tự cho robot thật:

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py \
  map:=/path/to/map.yaml \
  use_rviz:=true
```

## Gợi ý workflow

1. Khởi động robot hoặc simulator nền.
2. Nếu cần mapping, chạy `slam_demo.launch.py`.
3. Lưu map bằng `map_saver_cli`.
4. Chạy `sim_demo.launch.py` hoặc `real_robot_demo.launch.py`.

## Cấu trúc thư mục

```text
tb4_bringup/
├── launch/
│   ├── slam_demo.launch.py
│   ├── sim_demo.launch.py
│   └── real_robot_demo.launch.py
├── tb4_bringup/
│   └── launch_utils.py              # Helper tìm default map/params/rviz config
├── package.xml
├── setup.py
└── README.md
```
