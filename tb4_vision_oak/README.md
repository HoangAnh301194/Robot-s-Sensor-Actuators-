# 📦 tb4_vision_oak

## Tổng quan

`tb4_vision_oak` chạy object detection từ ảnh RGB trên topic `/oakd/rgb/preview/image_raw` bằng **YOLOv8n** (ultralytics) và publish bounding boxes 2D cho các module downstream.

## Node chính

- Executable: `detection_node`
- Mã nguồn chính: `tb4_vision_oak/detection_node.py`
- Wrapper tương thích: `scripts/detection_node.py`

## Parameters

Được nạp từ `config/camera_params.yaml`.

- `confidence_threshold`: ngưỡng chấp nhận detection (default: `0.5`)
- `show_debug_window`: bật/tắt cửa sổ OpenCV (default: `false`)
- `publish_debug_image`: bật/tắt publish ảnh debug (default: `true`)

Mặc định `show_debug_window=false` để launch được cả ở môi trường headless.

## Topics

- Subscribe: `/oakd/rgb/preview/image_raw` (`sensor_msgs/Image`)
- Publish: `/vision/detected_objects` (`vision_msgs/Detection2DArray`)
- Publish: `/vision/debug_image` (`sensor_msgs/Image`)

## Model

Luôn sử dụng `yolov8n.pt` (COCO 80 classes). Nếu `models/yolov8n.pt` tồn tại trong package thì node dùng file local; nếu chưa có, Ultralytics sẽ tự download model lần đầu chạy.

## Chạy module

```bash
colcon build --packages-select tb4_vision_oak
source install/setup.bash
ros2 launch tb4_vision_oak oak_detection.launch.py
```

Bật cửa sổ debug nếu cần:

```bash
ros2 launch tb4_vision_oak oak_detection.launch.py show_debug_window:=true
```

Tắt publish ảnh debug nếu muốn giảm tải:

```bash
ros2 launch tb4_vision_oak oak_detection.launch.py publish_debug_image:=false
```
