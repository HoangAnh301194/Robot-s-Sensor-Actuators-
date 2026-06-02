# 📦 tb4_nav_patrol (Nav2 Patrol & Simulation)

## 📖 1. Tổng quan (Overview)

`tb4_nav_patrol` là package ROS 2 (Humble) chịu trách nhiệm:

- Cấu hình Navigation2 (Nav2) cho TurtleBot 4 Lite
- Thiết lập hành vi tuần tra tự động trong bản đồ đã biết
- Quản lý map và localization (AMCL)
- Cung cấp launch file cho mô phỏng Gazebo

---

## 🏗️ 2. Kiến trúc Node

### Node: `patrol_node`

- **File thực thi:** `scripts/patrol_node.py`
- **Trạng thái:** ✅ Hoàn thành

### Chức năng chính

- Sử dụng `ActionClient` để giao tiếp với Nav2 (`NavigateToPose`)
- Quản lý danh sách waypoints (x, y, w)
- Tự động chuyển sang waypoint tiếp theo khi đến đích
- Tạm dừng 2 giây giữa các waypoint

---

## 📡 3. Giao tiếp Topics

| Topic | Msg Type | Mô tả |
|-------|----------|-------|
| `/navigate_to_pose` | `nav2_msgs/NavigateToPose` | Action goal gửi cho Nav2 |
| `/map` | `nav_msgs/OccupancyGrid` | Bản đồ occupancy grid |
| `/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | Vị trí hiện tại của robot |

---

## 📂 4. Cấu trúc thư mục

```
tb4_nav_patrol/
├── launch/
│   └── nav_patrol.launch.py        # Launch Nav2 + patrol node
├── config/                          # Nav2 config files, map files
├── scripts/
│   └── patrol_node.py              # Node logic tuần tra (Action Client)
└── README.md                        # Tài liệu này
```

---

## 🔨 5. Build & Run

```bash
# Build
colcon build --packages-select tb4_nav_patrol
source install/setup.bash

# Chạy
ros2 launch tb4_nav_patrol nav_patrol.launch.py
```

---

## 📚 6. Tài liệu tham khảo

- [Nav2 Documentation](https://docs.nav2.org/)
- [TurtleBot 4 Guide](https://turtlebot.github.io/turtlebot4-user-manual/)
- [Nav2 Waypoint Follower](https://docs.nav2.org/configuration/packages/configuring-waypoint-follower.html)
