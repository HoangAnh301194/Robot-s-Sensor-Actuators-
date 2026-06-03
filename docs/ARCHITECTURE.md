# Kiến trúc hệ thống

## Tổng quan

```text
camera RGB/depth
        |
        v
tb4_vision_oak  --->  /vision/detected_objects
        |
        v
tb4_object_localization  --->  /target_object_pose_map + TF detected_object_3d
        |
        v
tb4_mission_manager --(pause patrol + send safe goal)--> Nav2
        ^
        |
tb4_nav_patrol --(waypoint goals)-----------------------> Nav2
```

`tb4_bringup` là lớp orchestration, chịu trách nhiệm khởi động Nav2/localization và ghép toàn bộ module ứng dụng.

## Luồng hoạt động

1. `tb4_nav_patrol` gửi waypoint để robot tuần tra.
2. `tb4_vision_oak` phát hiện vật thể từ ảnh RGB.
3. `tb4_object_localization` dùng detection + depth để tính pose 3D tương đối.
4. `tb4_mission_manager` đổi pose mục tiêu sang `map`, publish `false` lên `/mission_manager/patrol_enabled`, rồi takeover `navigate_to_pose`.
5. Sau khi đến vị trí an toàn, `tb4_mission_manager` trả quyền tuần tra lại bằng `true`.

## Topics

| Topic | Producer | Consumer | Msg Type |
|-------|----------|----------|----------|
| `/oakd/rgb/preview/image_raw` | OAK-D | tb4_vision_oak | `sensor_msgs/Image` |
| `/oakd/rgb/preview/depth` | OAK-D | tb4_object_localization | `sensor_msgs/Image` |
| `/oakd/rgb/preview/camera_info` | OAK-D | tb4_object_localization | `sensor_msgs/CameraInfo` |
| `/vision/detected_objects` | tb4_vision_oak | tb4_object_localization | `vision_msgs/Detection2DArray` |
| `/target_object_pose_map` | tb4_object_localization | tb4_mission_manager | `geometry_msgs/PoseStamped` |
| `/mission_manager/patrol_enabled` | tb4_mission_manager | tb4_nav_patrol | `std_msgs/Bool` |

## Actions

| Action | Clients |
|--------|---------|
| `navigate_to_pose` | tb4_nav_patrol, tb4_mission_manager |

## TF liên quan

```text
map
 └── odom
      └── base_link
           └── oakd_link
                └── detected_object_3d
```

`tb4_object_localization` publish `detected_object_3d` trong frame `oakd_link`. `tb4_mission_manager` chịu trách nhiệm transform mục tiêu sang `map`.
