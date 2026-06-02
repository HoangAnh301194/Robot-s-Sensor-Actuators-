# 📦 tb4_mission_manager (Mission Management & Goal Generation)

## 📖 1. Tổng quan (Overview)

`tb4_mission_manager` là package ROS 2 (Humble) chịu trách nhiệm:

- Quản lý trạng thái hệ thống (state machine)
- Sinh goal tiếp cận an toàn dựa trên vị trí vật thể 3D
- Điều phối luồng hoạt động: tuần tra → phát hiện → tiếp cận → dừng an toàn → tiếp tục tuần tra
- Gửi goal cho Nav2 và xử lý feedback

---

## 🏗️ 2. Kiến trúc Node

### Node: `mission_manager_node`

- **File thực thi:** `scripts/mission_manager_node.py`
- **Trạng thái:** ✅ Hoàn thành

### Chức năng chính

- Subscribe tọa độ vật thể từ topic `/target_object_pose_map`
- Tính toán safe goal cách vật thể 0.5 mét
- Publish goal đến topic `/goal_pose` cho Nav2

### Logic tính toán Safe Goal

```python
distance = sqrt(obj_x^2 + obj_y^2)
if distance > safe_distance:
    ratio = (distance - safe_distance) / distance
    goal_x = obj_x * ratio
    goal_y = obj_y * ratio
```

---

## 📡 3. Giao tiếp Topics

| Topic | Msg Type | Mô tả |
|-------|----------|-------|
| `/target_object_pose_map` | `geometry_msgs/PoseStamped` | Nhận vị trí 3D vật thể từ tb4_object_localization |
| `/goal_pose` | `geometry_msgs/PoseStamped` | Gửi goal tiếp cận cho Nav2 |

---

## 📂 4. Cấu trúc thư mục

```
tb4_mission_manager/
├── launch/
│   └── mission_manager.launch.py    # Launch mission manager node
├── config/                          # Goal generation parameters
├── scripts/
│   └── mission_manager_node.py     # Logic sinh safe goal
└── README.md                        # Tài liệu này
```

---

## 🔨 5. Build & Run

```bash
# Build
colcon build --packages-select tb4_mission_manager
source install/setup.bash

# Chạy
ros2 launch tb4_mission_manager mission_manager.launch.py
```

---

## 📚 6. Tài liệu tham khảo

- [Nav2 Goal API](https://docs.nav2.org/)
- [ROS 2 Actions](https://docs.ros.org/en/humble/Concepts/Intermediate/Actions.html)
