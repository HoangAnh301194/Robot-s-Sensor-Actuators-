# 📦 tb4_vision_oak (OAK-D Lite Object Detection)

## 📖 1. Tổng quan (Overview)
`tb4_vision_oak` là một package ROS 2 (Humble) viết bằng Python thuộc hệ thống điều khiển robot TurtleBot 4. Gói này đóng vai trò là module thị giác máy tính (Vision AI), chịu trách nhiệm tiếp nhận luồng hình ảnh RGB từ camera OAK-D trong môi trường mô phỏng Gazebo, thực hiện nhận diện đối tượng bằng mô hình học sâu **MobileNet-SSD** qua OpenCV DNN và trích xuất thông tin bounding box 2D. 

Kết quả nhận diện này là đầu vào quan trọng để module định vị (`tb4_object_localization`) tính toán khoảng cách và tọa độ 3D của vật thể trong không gian.

---

## 🏗️ 2. Kiến trúc Node & Tham số (Node Architecture & Parameters)

### 🧩 Node: `oakd_detection_node`
* **File thực thi:** `scripts/detection_node.py` (được cấu hình cài đặt vào đường dẫn hệ thống qua `setup.py`).
* **Mô hình AI:** Khởi tạo mạng mạng nơ-ron thông qua OpenCV DNN (`cv2.dnn.readNetFromCaffe`), nạp trực tiếp cấu trúc mạng `.prototxt` và trọng số `.caffemodel`.

### ⚙️ Tham số cấu hình (ROS 2 Parameters)
Node quản lý và nạp cấu hình động thông qua file `config/camera_params.yaml`. Các tham số bao gồm:

| Tên tham số | Kiểu dữ liệu | Giá trị mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `confidence_threshold` | float | `0.5` | Ngưỡng độ tin cậy tối thiểu để chấp nhận một đối tượng đã nhận diện. |
| `camera_fps` | int | `30` | Tốc độ khung hình xử lý của camera. |
| `model_path` | string | `"models/mobilenet-ssd.blob"` | Đường dẫn trỏ tới file mô hình (sử dụng khi deploy trên phần cứng OAK-D thực tế). |

---

## 📡 3. Giao tiếp Topics (ROS 2 Topics)

### 📥 Subscribed Topics (Dữ liệu đầu vào)
* **`/oakd/rgb/preview/image_raw`** (`sensor_msgs/msg/Image`)
  * **Mô tả:** Tiếp nhận luồng dữ liệu hình ảnh RGB thô từ camera mô phỏng OAK-D gắn trên xe TurtleBot 4.
  * **Xử lý:** Node sử dụng thư viện `cv_bridge` để chuyển đổi tin nhắn ảnh dạng ROS sang ma trận BGR của `OpenCV` trước khi đưa vào mô hình AI.

### 📤 Published Topics (Dữ liệu đầu ra)
* **`/vision/detected_objects`** (`vision_msgs/msg/Detection2DArray` hoặc tùy biến theo hệ thống nhóm)
  * **Mô tả:** Xuất mảng chứa danh sách các vật thể được phát hiện kèm nhãn phân loại (Label), độ tin cậy (Confidence) và tọa độ pixel `(startX, startY, endX, endY)` của khung bao 2D (Bounding Box).
  * **Mục đích:** Cung cấp thông tin vùng ảnh mục tiêu cho Node định vị không gian 3D.

---

## 📂 4. Cấu trúc thư mục (Directory Structure)

```text
tb4_vision_oak/
├── config/
│   └── camera_params.yaml          # File cấu hình tham số Node (ngưỡng AI, FPS)
├── launch/
│   └── oak_detection.launch.py     # Script tự động nạp cấu hình và chạy Node
├── models/
│   ├── MobileNetSSD_deploy.prototxt   # Kiến trúc mạng MobileNet-SSD (Caffe)
│   ├── MobileNetSSD_deploy.caffemodel # Trọng số mô hình đã huấn luyện (Caffe)
│   └── mobilenet-ssd.blob             # Mô hình định dạng Myriad X (cho camera thực)
├── scripts/
│   └── detection_node.py           # Mã nguồn Python xử lý thuật toán nhận diện
├── package.xml                     # Khai báo dependencies (rclpy, sensor_msgs, cv_bridge)
├── setup.py                        # Cấu hình cài đặt và đóng gói tài nguyên ROS 2
└── README.md                       # Tài liệu hướng dẫn sử dụng package
