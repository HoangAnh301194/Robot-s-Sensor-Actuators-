# Kiến trúc hệ thống

## Tổng quát

```
                    ┌──────────────────┐
                    │  TurtleBot 4 Lite │
                    │ (base, odometry)  │
                    └────────┬──────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
       ┌────▼────┐   ┌──────▼──────┐   ┌─────▼────┐
       │   Nav2  │   │  OAK-D Lite │   │ Base Link│
       │         │   │   RGB-D     │   │   TF     │
       └────┬────┘   └──────┬──────┘   └─────┬────┘
            │                │                │
            │                ▼                │
            │        ┌────────────────┐       │
            │        │   tb4_vision   │       │
            │        │    _oak        │       │
            │        │ (detection)    │       │
            │        └────────┬───────┘       │
            │                 │               │
            │                 ▼               │
            │        ┌──────────────────┐     │
            │        │tb4_object_loc    │     │
            │        │alization         │     │
            │        │(3D pose, TF)     │     │
            │        └────────┬─────────┘     │
            │                 │               │
            │                 ▼               │
            │        ┌──────────────────┐     │
            │        │tb4_mission_      │     │
            │        │manager           │     │
            │        │(goal generation) │     │
            │        └────────┬─────────┘     │
            │                 │               │
            └────────────────►┼◄──────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  tb4_bringup      │
                    │  (orchestration)  │
                    └───────────────────┘
```

## Luồng dữ liệu

1. **Cảm biến**: Robot cung cấp odometry, TF tree
2. **Vision**: OAK-D camera → detection (bounding boxes)
3. **Localization**: depth + detection → 3D object pose + TF
4. **Mission**: object pose → safe goal → Nav2
5. **Navigation**: Nav2 lập kế hoạch & điều khiển robot

## ROS 2 Topics

| Topic | Producer | Consumer | Msg Type |
|-------|----------|----------|----------|
| `/camera/rgb/image_raw` | OAK-D | tb4_vision_oak | sensor_msgs/Image |
| `/camera/depth/image_raw` | OAK-D | tb4_object_loc | sensor_msgs/Image |
| `/detections` | tb4_vision_oak | tb4_mission_manager | custom/Detection[] |
| `/object_pose` | tb4_object_loc | tb4_mission_manager | geometry_msgs/PoseStamped |
| `/goal_poses` | tb4_mission_manager | Nav2 | geometry_msgs/PoseStamped |

## Cấu trúc TF

```
map
 └── odom
      └── base_footprint
           └── base_link
                ├── camera_link
                │   └── camera_optical_frame
                └── caster_wheel_link
```
