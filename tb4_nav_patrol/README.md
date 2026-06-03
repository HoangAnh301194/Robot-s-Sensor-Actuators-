# 📦 tb4_nav_patrol

## Tổng quan

`tb4_nav_patrol` chứa logic tuần tra waypoint bằng `NavigateToPose` action client.

Package này **không tự bring up Nav2** nữa. Nó giả định Nav2 đã được khởi động bởi `tb4_bringup` hoặc một navigation stack bên ngoài.

## Node chính

- Executable: `patrol_node`
- Mã nguồn chính: `tb4_nav_patrol/patrol_node.py`
- Wrapper tương thích: `scripts/patrol_node.py`

## Hành vi

- Gửi tuần tự các waypoint trong frame `map`
- Tự lặp lại sau waypoint cuối
- Tạm dừng khi nhận `false` từ topic `/mission_manager/patrol_enabled`
- Hủy goal hiện tại để nhường Nav2 cho `tb4_mission_manager`
- Tiếp tục tuần tra khi nhận lại `true`

## Giao tiếp

- Action client `navigate_to_pose`
- Topic subscribe `/mission_manager/patrol_enabled` (`std_msgs/Bool`)

## Chạy module

```bash
colcon build --packages-select tb4_nav_patrol
source install/setup.bash
ros2 launch tb4_nav_patrol nav_patrol.launch.py
```

Để chạy đầy đủ cùng Nav2, dùng:

```bash
ros2 launch tb4_bringup sim_demo.launch.py map:=/path/to/map.yaml
```
