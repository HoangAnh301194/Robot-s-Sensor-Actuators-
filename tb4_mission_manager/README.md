# 📦 tb4_mission_manager

## Tổng quan

`tb4_mission_manager` điều phối pha "phát hiện mục tiêu -> tiếp cận an toàn -> trả quyền tuần tra lại".

Node này nhận pose mục tiêu tương đối từ `tb4_object_localization`, biến đổi sang `map`, tính safe approach goal, rồi gửi trực tiếp đến Nav2 qua action `navigate_to_pose`.

## Node chính

- Executable: `mission_manager_node`
- Mã nguồn chính: `tb4_mission_manager/mission_manager_node.py`
- Wrapper tương thích: `scripts/mission_manager_node.py`

## Hành vi

- Subscribe `/target_object_pose_map`
- Lookup TF từ `oakd_link` sang `map`
- Tính goal cách mục tiêu một khoảng `safe_distance`
- Publish `false` lên `/mission_manager/patrol_enabled` để tạm dừng patrol
- Gửi goal tiếp cận qua `NavigateToPose`
- Khi xong, publish `true` để patrol tiếp tục
- Có cooldown ngắn để tránh re-trigger liên tục cùng một mục tiêu

## Parameters

- `safe_distance` mặc định `1.0`
- `target_cooldown_sec` mặc định `5.0`

## Chạy module

```bash
colcon build --packages-select tb4_mission_manager
source install/setup.bash
ros2 launch tb4_mission_manager mission_manager.launch.py
```
