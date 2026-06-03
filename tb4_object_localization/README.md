# 📦 tb4_object_localization (3D Object Localization)

## 📖 1. Tổng quan (Overview)
`tb4_object_localization` là một package ROS 2 (Humble) được viết bằng Python (tích hợp trong nền tảng hệ thống xây dựng `ament_cmake`). Gói này đóng vai trò là module định vị không gian 3D thuộc chuỗi xử lý tự hành của robot TurtleBot 4.

Module này tiếp nhận thông tin ma trận chiều sâu (Depth Map) và thông số kỹ thuật (Intrinsics) từ camera OAK-D mô phỏng, kết hợp với tọa độ pixel vùng nhận diện (2D Bounding Box) từ module thị giác (`tb4_vision_oak`) để tính toán chính xác khoảng cách và tọa độ vật lý $X, Y, Z$ của mục tiêu theo mô hình camera lỗ kim (Pinhole Camera Model). Sau đó, vị trí này được phát tán (broadcast) lên hệ thống dưới dạng một phối cảnh tọa độ động (TF Dynamic Transform) để hiển thị trực quan trên RViz2.

Với YOLOv8n, node ưu tiên detection class `person` (`class_id=0`) và publish thêm marker chấm tròn màu đỏ/cam trên topic `/target_object_marker` để debug trong RViz.

---

## 🏗️ 2. Kiến trúc Node (Node Architecture)

### 🧩 Node: `object_localization_node`
* **File thực thi:** `scripts/localization_node.py` (được cấu hình cài đặt thông qua `CMakeLists.txt`).
* **Cơ chế cốt lõi:** 1. Đọc ma trận camera từ `CameraInfo` để trích xuất các tiêu cự ($f_x, f_y$) và tâm quang học ($c_x, c_y$).
  2. Lắng nghe luồng ảnh Depth, trích xuất giá trị độ sâu $Z$ (đơn vị mm) tại tâm của đối tượng mục tiêu $(u, v)$.
  3. Áp dụng công thức hình chiếu ngược (Pinhole Camera Model) để chuyển đổi tọa độ pixel 2D sang tọa độ không gian 3D của camera:
     $$X_c = \frac{(u - c_x) \times Z}{f_x}$$
     $$Y_c = \frac{(v - c_y) \times Z}{f_y}$$
     $$Z_c = Z$$

---

## 📡 3. Giao tiếp Topics & Khung tọa độ (ROS 2 Topics & TF)

### 📥 Subscribed Topics (Dữ liệu đầu vào)
* **`/oakd/rgb/preview/camera_info`** (`sensor_msgs/msg/CameraInfo`)
  * **Mô tả:** Nhận các thông số nội tại (Intrinsic Parameters) của camera để lấy ma trận $K$ phục vụ tính toán hình học chiếu.
* **`/oakd/rgb/preview/depth`** (`sensor_msgs/msg/Image`)
  * **Mô tả:** Tiếp nhận luồng dữ liệu chiều sâu tương ứng với khung hình camera. Giá trị của mỗi pixel biểu thị khoảng cách từ camera đến bề mặt vật thể vật lý.
* **`/vision/detected_objects`** (`vision_msgs/msg/Detection2DArray`)
  * **Mô tả:** Nhận bounding box từ YOLOv8n; ưu tiên class `person` nếu có.

### 📤 Published Topics (Dữ liệu đầu ra)
* **`/target_object_pose_map`** (`geometry_msgs/msg/PoseStamped`)
  * **Mô tả:** Pose 3D của mục tiêu trong frame camera `oakd_link` để Mission Manager sử dụng.
* **`/target_object_marker`** (`visualization_msgs/msg/Marker`)
  * **Mô tả:** Chấm tròn debug mục tiêu/người trong RViz. RViz Fixed Frame có thể để `map` nếu cây TF `map -> ... -> oakd_link` đang đầy đủ.

### 📍 Cấu hình hệ tọa độ TF (Transform Broadcaster)
Node sử dụng `tf2_ros.TransformBroadcaster` để liên tục phát tọa độ vị trí của vật thể được phát hiện vào cây tọa độ chung của hệ thống:
* **Parent Frame (Khung gốc):** `oakd_link` (Hệ tọa độ của mắt camera gắn trên xe robot).
* **Child Frame (Khung vật thể):** `detected_object_3d` (Hệ tọa độ động của mục tiêu).
* **Ánh xạ hướng trục (Coordinate Mapping sang chuẩn ROS):**
  * Trục **X** (ROS hướng tới trước): Nhận giá trị từ trục $Z_c$ (khoảng cách chiều sâu).
  * Trục **Y** (ROS hướng sang trái): Nhận giá trị từ trục $-X_c$ (lệch ngang).
  * Trục **Z** (ROS hướng lên trên): Nhận giá trị từ trục $-Y_c$ (độ cao vật thể).

---

## 📂 4. Cấu trúc thư mục (Directory Structure)

```text
tb4_object_localization/
├── launch/
│   └── localization.launch.py      # Script tự động khởi chạy node định vị
├── scripts/
│   └── localization_node.py        # Mã nguồn xử lý toán học toán định vị 3D và phát TF
├── CMakeLists.txt                  # Cấu hình biên dịch và cài đặt scripts/launch theo chuẩn CMake
├── package.xml                     # Khai báo các dependencies của hệ thống (tf2_ros, geometry_msgs,...)
└── README.md                       # Tài liệu hướng dẫn sử dụng package
