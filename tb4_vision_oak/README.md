# 📦 tb4_vision_oak (OAK-D Lite Object Detection)

## 📖 1. Tổng quan (Overview)
`tb4_vision_oak` là một package ROS 2 (Humble) viết bằng Python thuộc hệ thống điều khiển robot TurtleBot 4. Gói này đóng vai trò là module thị giác máy tính (Vision AI), chịu trách nhiệm tiếp nhận luồng hình ảnh RGB từ camera OAK-D trong môi trường mô phỏng Gazebo, thực hiện nhận diện đối tượng bằng bộ mô hình học sâu tiên tiến **YOLOv8** thông qua thư viện `ultralytics` và trích xuất thông tin bounding box 2D. 

So với MobileNet-SSD cũ, YOLOv8 cung cấp độ chính xác vượt trội, khả năng bắt hình mượt mà hơn và hỗ trợ tới 80 lớp vật thể khác nhau (tập dữ liệu COCO). Kết quả nhận diện này là đầu vào quan trọng để module định vị (`tb4_object_localization`) tính toán khoảng cách và tọa độ 3D của vật thể trong không gian.

---

## 🏗️ 2. Kiến trúc Node & Tham số (Node Architecture & Parameters)

### 🧩 Node: `oakd_detection_node`
* **File thực thi:** `scripts/detection_node.py` (được cấu hình cài đặt vào đường dẫn hệ thống qua `setup.py`).
* **Mô hình AI:** Khởi tạo mạng mạng nơ-ron thông qua lớp `YOLO()` của thư viện `ultralytics`. 
  * *Trong môi trường mô phỏng:* Nạp trực tiếp trọng số `.pt` chạy trên tài nguyên CPU/GPU của máy tính.
  * *Trên robot thực tế:* Cấu hình pipeline của thư viện DepthAI để nạp mô hình `.blob` chạy trực tiếp trên chip Myriad X (VPU) của camera OAK-D.

### ⚙️ Tham số cấu hình (ROS 2 Parameters)
Node quản lý và nạp cấu hình động thông qua file `config/camera_params.yaml`. Các tham số bao gồm:

| Tên tham số | Kiểu dữ liệu | Giá trị mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `confidence_threshold` | float | `0.5` | Ngưỡng độ tin cậy (Confidence) tối thiểu để giữ lại một khung nhận diện. |
| `camera_fps` | int | `30` | Tốc độ khung hình xử lý của camera. |
| `model_path` | string | `"/home/nhatnguyen/tb4_project_ab/src/Robot-s-Sensor-Actuators-/tb4_vision_oak/models/yolov8n.pt"` | Đường dẫn tuyệt đối trỏ tới file mô hình (nạp `.pt` cho Gazebo hoặc `.blob` cho xe thật). |

---

## 📡 3. Giao tiếp Topics (ROS 2 Topics)

### 📥 Subscribed Topics (Dữ liệu đầu vào)
* **`/oakd/rgb/preview/image_raw`** (`sensor_msgs/msg/Image`)
  * **Mô tả:** Tiếp nhận luồng dữ liệu hình ảnh RGB thô từ camera mô phỏng OAK-D gắn trên xe TurtleBot 4.
  * **Xử lý:** Node sử dụng thư viện `cv_bridge` để chuyển đổi tin nhắn ảnh dạng ROS sang format OpenCV (BGR) trước khi đưa vào mô hình YOLOv8 để nội suy.

### 📤 Published Topics (Dữ liệu đầu ra)
* **`/vision/detected_objects`** (`vision_msgs/msg/Detection2DArray` hoặc tùy biến theo hệ thống nhóm)
  * **Mô tả:** Xuất mảng chứa danh sách các vật thể được phát hiện kèm nhãn phân loại (Label), độ tin cậy (Confidence) và tọa độ pixel `(startX, startY, endX, endY)` của khung bao 2D.
  * **Mục đích:** Cung cấp thông tin vùng ảnh mục tiêu cho Node định vị không gian 3D.

---

## 📂 4. Cấu trúc thư mục (Directory Structure)

```text
tb4_vision_oak/
├── config/
│   └── camera_params.yaml        # File cấu hình tham số Node (đường dẫn model, ngưỡng AI)
├── launch/
│   └── oak_detection.launch.py   # Script tự động nạp cấu hình và chạy Node
├── models/
│   ├── yolov8n.pt                # Trọng số YOLOv8 gốc của PyTorch (dùng cho Gazebo)
│   ├── yolov8n.onnx              # File cấu trúc trung gian (opset 12)
│   └── yolov8n.blob              # Mô hình biên dịch qua OpenVINO (chạy trên chip camera thật)
├── scripts/
│   └── detection_node.py         # Mã nguồn Python xử lý thuật toán nhận diện YOLOv8
├── package.xml                   # Khai báo dependencies (rclpy, sensor_msgs, cv_bridge)
├── setup.py                      # Cấu hình cài đặt và đóng gói tài nguyên ROS 2
└── README.md                     # Tài liệu hướng dẫn sử dụng package
```
