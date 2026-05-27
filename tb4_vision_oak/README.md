# tb4_vision_oak - OAK-D-Lite Object Detection

## Mô tả module

Module này chịu trách nhiệm:
- Tích hợp camera OAK-D-Lite RGB-D
- Chạy mô hình object detection tối ưu cho edge
- Xử lý ảnh RGB và depth
- Publish detection results via ROS 2 topics

## Cấu trúc thư mục

```
tb4_vision_oak/
├── launch/          # Launch files cho OAK-D
├── config/          # Camera config, model config
├── scripts/         # Object detection scripts
├── models/          # Pre-trained models (YOLO, etc.)
└── README.md        # Tài liệu module
```

## Thành viên chịu trách nhiệm

- **Member 2**: OAK-D-Lite & object detection

## Công việc cần làm

- [ ] Cấu hình OAK-D camera driver
- [ ] Download/convert detection model
- [ ] Viết inference script
- [ ] Publish detection ROS 2 topics
- [ ] Tạo launch file

## Tài liệu

- [OAK-D Documentation](https://docs.luxonis.com/)
- [YOLOv8 Edge](https://docs.ultralytics.com/)
