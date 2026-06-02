# Kiến trúc hệ thống

## Tổng quan

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

## Luồng dữ liệu

1. **Cảm biến**: Robot cung cấp odometry, TF tree
2. **Vision**: OAK-D camera → detection (bounding boxes)
3. **Localization**: depth + detection → 3D object pose + TF
4. **Mission**: object pose → safe goal → Nav2
5. **Navigation**: Nav2 lập kế hoạch & điều khiển robot

## ROS 2 Topics

| Topic | Producer | Consumer | Msg Type |
|-------|----------|----------|----------|
| `/oakd/rgb/preview/image_raw` | OAK-D | tb4_vision_oak | sensor_msgs/Image |
| `/oakd/rgb/preview/depth` | OAK-D | tb4_object_localization | sensor_msgs/Image |
| `/oakd/rgb/preview/camera_info` | OAK-D | tb4_object_localization | sensor_msgs/CameraInfo |
| `/vision/detected_objects` | tb4_vision_oak | tb4_mission_manager | vision_msgs/Detection2DArray |
| `/target_object_pose_map` | tb4_object_localization | tb4_mission_manager | geometry_msgs/PoseStamped |
| `/goal_pose` | tb4_mission_manager | Nav2 | geometry_msgs/PoseStamped |
| `/navigate_to_pose` | Nav2 | tb4_nav_patrol | nav2_msgs/NavigateToPose |

## Cấu trúc TF

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

## Trạng thái triển khai

| Module | Trạng thái | Ghi chú |
|--------|-----------|---------|
| tb4_vision_oak | ✅ Hoàn thành | MobileNet-SSD, OpenCV DNN |
| tb4_object_localization | ✅ Hoàn thành | Pinhole model, TF broadcast |
| tb4_nav_patrol | ✅ Hoàn thành | Nav2 Action Client, waypoint navigation |
| tb4_mission_manager | ✅ Hoàn thành | Safe goal generation |
| tb4_bringup | ✅ Hoàn thành | Launch file orchestration + RViz2 |
