# Giàn Ý Báo Cáo Nghiên Cứu Dự Án TurtleBot4

## Tên đề tài gợi ý

**Nghiên cứu và xây dựng hệ thống robot tự hành TurtleBot4 trong môi trường mô phỏng sử dụng ROS2, SLAM, Nav2 và YOLOv8**

Hoặc:

**Xây dựng hệ thống robot tự hành TurtleBot4 với khả năng tuần tra, nhận diện và tiếp cận mục tiêu trong ROS2**

---

# Chương 1: Tổng Quan Đề Tài

## 1.1 Bối cảnh nghiên cứu

- Sự phát triển của robot tự hành trong kho vận, nhà máy, dịch vụ, giám sát và hỗ trợ con người.
- Vai trò của robot di động trong các bài toán tuần tra, định vị, nhận diện và tiếp cận mục tiêu.
- Nhu cầu mô phỏng robot trước khi triển khai trên phần cứng thật nhằm giảm chi phí và rủi ro.

## 1.2 Lý do chọn đề tài

- TurtleBot4 là nền tảng phổ biến để nghiên cứu robot tự hành.
- ROS2 hỗ trợ tốt cho hệ thống robot phân tán, realtime và mở rộng module.
- Gazebo/Ignition cho phép mô phỏng cảm biến, môi trường và robot tương đối sát thực tế.
- YOLOv8 hỗ trợ nhận diện vật thể nhanh, phù hợp với bài toán phát hiện người hoặc mục tiêu.

## 1.3 Mục tiêu của đề tài

- Xây dựng môi trường mô phỏng TurtleBot4 Lite trong Gazebo/Ignition.
- Thu thập dữ liệu cảm biến như LiDAR, camera RGB-D, odometry và TF.
- Thực hiện SLAM để xây dựng bản đồ môi trường.
- Sử dụng Nav2 để điều hướng robot trong bản đồ đã có.
- Tích hợp YOLOv8n để nhận diện người hoặc vật thể.
- Định vị mục tiêu trong không gian 3D dựa trên ảnh RGB, ảnh depth và camera intrinsic.
- Xây dựng Mission Manager để điều phối hành vi tuần tra, phát hiện và tiếp cận mục tiêu.

## 1.4 Phạm vi nghiên cứu

- Hệ thống được triển khai trên ROS2 Humble.
- Robot sử dụng trong mô phỏng là TurtleBot4 Lite.
- Môi trường thử nghiệm chính là warehouse trong Gazebo/Ignition.
- Nhận diện vật thể sử dụng YOLOv8n pretrained trên COCO dataset.
- Hệ thống tập trung vào mô phỏng, chưa triển khai trên robot thật.

## 1.5 Kết quả mong muốn

- Robot spawn thành công trong môi trường mô phỏng.
- LiDAR, camera, odometry và TF hoạt động ổn định.
- Robot có thể xây dựng và lưu bản đồ bằng SLAM.
- Robot có thể điều hướng bằng Nav2.
- Robot có thể nhận diện mục tiêu bằng YOLOv8n.
- Robot có thể hiển thị vị trí mục tiêu bằng marker trong RViz.
- Robot có thể tuần tra, phát hiện mục tiêu, tiếp cận mục tiêu và quay lại tuần tra.

---

# Chương 2: Cơ Sở Lý Thuyết

## 2.1 Tổng quan về robot tự hành

- Khái niệm robot tự hành.
- Các thành phần chính của robot tự hành:
  - Nhận thức môi trường.
  - Định vị.
  - Lập bản đồ.
  - Lập kế hoạch đường đi.
  - Điều khiển chuyển động.
  - Ra quyết định nhiệm vụ.

## 2.2 ROS2

- Giới thiệu ROS2.
- Các khái niệm chính:
  - Node.
  - Topic.
  - Message.
  - Service.
  - Action.
  - Parameter.
  - Launch file.
- Cơ chế giao tiếp DDS trong ROS2.
- Vai trò của ROS2 trong hệ thống robot module hóa.

## 2.3 TF và hệ tọa độ trong robot

- Khái niệm frame.
- Quan hệ giữa các frame:
  - `map`.
  - `odom`.
  - `base_link`.
  - `oakd_link`.
  - `rplidar_link`.
- Vai trò của TF/TF2 trong định vị, navigation và visualization.

## 2.4 Mô phỏng robot với Gazebo/Ignition

- Vai trò của mô phỏng trong phát triển robot.
- Mô phỏng môi trường, robot và cảm biến.
- TurtleBot4 trong Gazebo/Ignition.
- Các topic mô phỏng quan trọng:
  - `/clock`.
  - `/scan`.
  - `/odom`.
  - `/tf`.
  - `/oakd/rgb/preview/image_raw`.
  - `/oakd/rgb/preview/depth`.

## 2.5 Cảm biến sử dụng trong hệ thống

- LiDAR:
  - Nguyên lý đo khoảng cách.
  - Vai trò trong SLAM và tránh vật cản.
- Camera RGB:
  - Cung cấp ảnh màu cho nhận diện vật thể.
- Camera depth:
  - Cung cấp khoảng cách từ camera tới vật thể.
- Odometry:
  - Ước lượng chuyển động của robot.

## 2.6 SLAM

- Khái niệm Simultaneous Localization and Mapping.
- Dữ liệu đầu vào của SLAM:
  - LaserScan.
  - Odometry.
  - TF.
- `slam_toolbox` trong ROS2.
- Bản đồ occupancy grid.
- Lưu bản đồ bằng `map_saver_cli`.

## 2.7 Navigation với Nav2

- Tổng quan Nav2.
- Các thành phần chính:
  - Map server.
  - AMCL.
  - Planner server.
  - Controller server.
  - Behavior tree navigator.
  - Costmap.
- Action `NavigateToPose`.
- Điều hướng robot tới waypoint hoặc mục tiêu.

## 2.8 Nhận diện vật thể với YOLOv8n

- Tổng quan YOLO.
- YOLOv8n và ưu điểm của mô hình nhẹ.
- Bounding box, class ID và confidence score.
- Ứng dụng YOLO trong bài toán phát hiện người/vật thể trên robot.

## 2.9 Định vị mục tiêu bằng RGB-D camera

- Mô hình camera pinhole.
- Camera intrinsic:
  - `fx`.
  - `fy`.
  - `cx`.
  - `cy`.
- Tính tọa độ 3D từ pixel ảnh và depth.
- Chuyển đổi tọa độ giữa camera frame, robot frame và map frame.

---

# Chương 3: Phân Tích Và Thiết Kế Hệ Thống

## 3.1 Yêu cầu hệ thống

- Robot phải chạy được trong mô phỏng.
- Robot phải có dữ liệu LiDAR, odometry, camera và TF.
- Robot phải xây dựng được bản đồ bằng SLAM.
- Robot phải điều hướng được bằng Nav2.
- Robot phải nhận diện được mục tiêu bằng YOLOv8n.
- Robot phải định vị được mục tiêu bằng depth camera.
- Robot phải có logic điều phối nhiệm vụ tự động.

## 3.2 Kiến trúc tổng thể

```text
Gazebo/Ignition Simulation
        ↓
/scan, /odom, /tf, /camera
        ↓
SLAM / Nav2 / YOLO Detection
        ↓
Object Localization
        ↓
Mission Manager
        ↓
Patrol / Approach Target
        ↓
Nav2 NavigateToPose
```

## 3.3 Các module trong hệ thống

- `tb4_bringup`: gom launch file và chạy full stack.
- `tb4_vision_oak`: nhận diện vật thể bằng YOLOv8n.
- `tb4_object_localization`: tính vị trí 3D của mục tiêu.
- `tb4_nav_patrol`: tuần tra theo waypoint.
- `tb4_mission_manager`: điều phối nhiệm vụ phát hiện và tiếp cận mục tiêu.

## 3.4 Luồng dữ liệu ROS2

- Camera RGB publish ảnh qua `/oakd/rgb/preview/image_raw`.
- YOLO node subscribe ảnh RGB và publish `/vision/detected_objects`.
- Object localization node nhận detection, depth và camera info.
- Object localization node publish `/target_object_pose_map` và `/target_object_marker`.
- Mission manager subscribe `/target_object_pose_map`.
- Mission manager điều khiển patrol qua `/mission_manager/patrol_enabled`.
- Patrol node gửi goal tới Nav2 bằng `NavigateToPose`.
- Mission manager cũng gửi goal tới Nav2 khi cần tiếp cận mục tiêu.

## 3.5 Thiết kế hành vi robot

- Trạng thái tuần tra:
  - Robot đi qua các waypoint định trước.
- Trạng thái phát hiện mục tiêu:
  - Hệ thống nhận diện mục tiêu bằng YOLOv8n.
  - Hệ thống tính vị trí mục tiêu dựa trên depth.
- Trạng thái tiếp cận mục tiêu:
  - Mission manager tạm dừng patrol.
  - Robot đi tới điểm cách mục tiêu một khoảng an toàn.
- Trạng thái quay lại tuần tra:
  - Sau khi tiếp cận xong, mission manager bật lại patrol.

---

# Chương 4: Xây Dựng Môi Trường Mô Phỏng Và Bản Đồ

## 4.1 Cài đặt môi trường

- Ubuntu.
- ROS2 Humble.
- TurtleBot4 packages.
- Gazebo/Ignition.
- Python dependencies.
- Workspace `tb4_project_ab`.

## 4.2 Build workspace

- Source ROS2 Humble.
- Build bằng `colcon build --symlink-install`.
- Source workspace sau khi build.

## 4.3 Launch mô phỏng TurtleBot4

- Launch TurtleBot4 Lite trong warehouse world.
- Thiết lập `ROS_DOMAIN_ID`.
- Tắt shared memory FastDDS nếu cần bằng `RMW_FASTRTPS_USE_SHM=0`.

## 4.4 Kiểm tra dữ liệu cảm biến

- Kiểm tra `/clock`.
- Kiểm tra `/scan`.
- Kiểm tra `/odom`.
- Kiểm tra `/tf`.
- Kiểm tra camera RGB và depth.

## 4.5 Debug lỗi mô phỏng đã gặp

- Lỗi session cũ còn sót.
- Lỗi ROS daemon cache.
- Lỗi FastDDS shared memory.
- Lỗi `/scan` toàn giá trị `0.164`.
- Lỗi LiDAR bị quá thấp hoặc bị collision với robot model.
- Cách kiểm tra và điều chỉnh offset RPLIDAR.

## 4.6 Chạy SLAM

- Chạy `slam_toolbox`.
- Điều khiển robot bằng teleop.
- Quan sát map trong RViz.
- Kiểm tra `/map`, `/scan`, `/tf`.

## 4.7 Lưu bản đồ

- Sử dụng `nav2_map_server map_saver_cli`.
- Kiểm tra file `.yaml` và `.pgm` sau khi lưu.
- Đánh giá bản đồ thu được.

---

# Chương 5: Xây Dựng Các Module Chức Năng

## 5.1 Module nhận diện vật thể `tb4_vision_oak`

### Chức năng

- Nhận ảnh RGB từ camera mô phỏng.
- Chạy YOLOv8n để phát hiện người hoặc vật thể.
- Publish bounding box và class ID.
- Publish ảnh debug đã vẽ bounding box.

### Input

- `/oakd/rgb/preview/image_raw`

### Output

- `/vision/detected_objects`
- `/vision/debug_image`

### Nội dung xử lý

- Chuyển ROS Image sang OpenCV image.
- Chạy YOLOv8n inference.
- Lọc kết quả theo confidence threshold.
- Đóng gói kết quả thành `Detection2DArray`.
- Publish ảnh debug để xem trên RViz.

## 5.2 Module định vị mục tiêu `tb4_object_localization`

### Chức năng

- Nhận detection từ YOLO.
- Lấy depth tại vùng bounding box.
- Tính tọa độ 3D của mục tiêu.
- Publish pose và marker của mục tiêu.

### Input

- `/vision/detected_objects`
- `/oakd/rgb/preview/depth`
- `/oakd/rgb/preview/camera_info`

### Output

- `/target_object_pose_map`
- `/target_object_marker`

### Nội dung xử lý

- Lấy tâm bounding box.
- Lấy median depth quanh tâm bounding box.
- Tính tọa độ 3D bằng mô hình camera pinhole.
- Chuyển hệ trục camera sang hệ trục ROS.
- Publish marker để debug trong RViz.

## 5.3 Module tuần tra `tb4_nav_patrol`

### Chức năng

- Điều khiển robot đi tuần tra theo các waypoint định trước.
- Gửi goal tới Nav2 thông qua `NavigateToPose`.
- Tạm dừng hoặc tiếp tục tuần tra theo lệnh từ mission manager.

### Input

- `/mission_manager/patrol_enabled`

### Output

- Goal gửi tới Nav2 action `navigate_to_pose`.

### Hành vi

- Khi nhận `true`: tiếp tục tuần tra.
- Khi nhận `false`: hủy goal hiện tại và dừng tuần tra.

## 5.4 Module điều phối nhiệm vụ `tb4_mission_manager`

### Chức năng

- Điều phối giữa patrol và target approach.
- Khi phát hiện mục tiêu, tạm dừng patrol.
- Tính điểm tiếp cận an toàn.
- Gửi goal tới Nav2.
- Sau khi hoàn thành, bật lại patrol.

### Input

- `/target_object_pose_map`

### Output

- `/mission_manager/patrol_enabled`
- Goal gửi tới Nav2 action `navigate_to_pose`.

### Logic hoạt động

- Nếu đang patrol và nhận được mục tiêu hợp lệ:
  - Transform vị trí mục tiêu sang map frame.
  - Tính điểm cách mục tiêu `safe_distance`.
  - Publish `false` để tắt patrol.
  - Gửi goal tới Nav2.
- Khi goal kết thúc:
  - Chờ cooldown.
  - Publish `true` để bật lại patrol.

## 5.5 Module bringup `tb4_bringup`

### Chức năng

- Gom các launch file thành một launch tổng.
- Chạy localization, Nav2, detection, object localization, patrol, mission manager và RViz.

### Thành phần được launch

- TurtleBot4 localization.
- Nav2.
- Initial pose publisher.
- YOLO detection.
- Object localization.
- Mission manager.
- Patrol.
- RViz debug.

---

# Chương 6: Thử Nghiệm Và Đánh Giá

## 6.1 Kịch bản thử nghiệm mô phỏng

- Launch Gazebo/Ignition.
- Kiểm tra robot spawn đúng.
- Kiểm tra robot có thể điều khiển bằng teleop.
- Kiểm tra các topic cảm biến.

## 6.2 Kịch bản thử nghiệm SLAM

- Chạy SLAM.
- Điều khiển robot di chuyển trong warehouse.
- Quan sát bản đồ mở rộng trong RViz.
- Lưu bản đồ.
- Kiểm tra kích thước và nội dung bản đồ đã lưu.

## 6.3 Kịch bản thử nghiệm Nav2

- Load bản đồ đã lưu.
- Chạy localization và Nav2.
- Publish initial pose.
- Gửi goal thủ công trong RViz.
- Đánh giá khả năng lập kế hoạch và di chuyển.

## 6.4 Kịch bản thử nghiệm nhận diện vật thể

- Chạy module YOLOv8n.
- Kiểm tra `/vision/detected_objects`.
- Kiểm tra `/vision/debug_image`.
- Quan sát bounding box trong RViz hoặc OpenCV window.

## 6.5 Kịch bản thử nghiệm định vị mục tiêu

- Chạy object localization.
- Kiểm tra depth image và camera info.
- Kiểm tra `/target_object_pose_map`.
- Hiển thị `/target_object_marker` trong RViz.

## 6.6 Kịch bản thử nghiệm full mission

- Launch simulator.
- Launch full stack bằng `tb4_bringup sim_demo.launch.py`.
- Robot bắt đầu tuần tra theo waypoint.
- Khi phát hiện mục tiêu:
  - Patrol tạm dừng.
  - Robot tiếp cận mục tiêu.
  - Sau khi hoàn thành, robot quay lại tuần tra.

## 6.7 Đánh giá kết quả

- Độ ổn định của mô phỏng.
- Độ tin cậy của dữ liệu LiDAR.
- Chất lượng bản đồ SLAM.
- Khả năng điều hướng của Nav2.
- Tốc độ và độ chính xác của YOLOv8n.
- Độ hợp lý của vị trí mục tiêu tính từ depth.
- Khả năng phối hợp giữa patrol và mission manager.

## 6.8 Hạn chế trong quá trình thử nghiệm

- Một số lỗi phụ thuộc vào session cũ hoặc ROS daemon cache.
- LiDAR có thể bị lỗi nếu vị trí cảm biến trong URDF chưa phù hợp.
- Độ chính xác target localization phụ thuộc vào depth image.
- Waypoint patrol hiện còn cố định trong source code.
- Hệ thống mới kiểm thử trong mô phỏng, chưa kiểm thử trên robot thật.

---

# Chương 7: Kết Luận Và Hướng Phát Triển

## 7.1 Kết luận

- Đề tài đã xây dựng được hệ thống mô phỏng TurtleBot4 trên ROS2.
- Hệ thống có khả năng đọc dữ liệu LiDAR, camera, depth, odometry và TF.
- Robot có thể xây dựng bản đồ bằng SLAM.
- Robot có thể điều hướng bằng Nav2.
- YOLOv8n được tích hợp để nhận diện mục tiêu.
- Object localization tính được vị trí mục tiêu từ detection và depth.
- Mission manager điều phối được quá trình tuần tra, phát hiện và tiếp cận mục tiêu.

## 7.2 Các kết quả đạt được

- Xây dựng workspace ROS2 gồm nhiều package chức năng.
- Tích hợp mô phỏng TurtleBot4 với Gazebo/Ignition.
- Debug và khắc phục lỗi LiDAR scan.
- Tích hợp YOLOv8n thay cho MobileNetSSD.
- Hiển thị debug bằng RViz thông qua image, laser scan, TF, map và marker.
- Xây dựng luồng full mission từ patrol tới target approach.

## 7.3 Hạn chế

- Chưa triển khai trên TurtleBot4 thật.
- Chưa tối ưu toàn bộ Nav2 parameters.
- Patrol waypoint còn hardcode.
- Mission manager mới ở dạng logic đơn giản, chưa phải state machine phức tạp.
- Robot chưa xoay mặt tối ưu về phía mục tiêu khi tiếp cận.
- Chưa có tracking nhiều mục tiêu hoặc mục tiêu động.

## 7.4 Hướng phát triển

- Triển khai và kiểm thử trên robot thật.
- Tối ưu Nav2 costmap, planner và controller.
- Đưa waypoint patrol ra file YAML.
- Xây dựng Mission Manager theo finite state machine hoặc behavior tree.
- Thêm khả năng theo dõi mục tiêu động.
- Thêm multi-object tracking.
- Huấn luyện YOLO model custom cho đối tượng chuyên biệt.
- Tích hợp semantic map.
- Cải thiện visualization dashboard trong RViz.
- Thêm logging và đánh giá định lượng cho từng module.

---

# Phụ Lục A: Cấu Trúc Source Code

```text
tb4_project_ab/
├── src/
│   └── Robots_Sensor_Actuators/
│       ├── tb4_bringup/
│       ├── tb4_vision_oak/
│       ├── tb4_object_localization/
│       ├── tb4_nav_patrol/
│       └── tb4_mission_manager/
```

---

# Phụ Lục B: Các Lệnh Chạy Chính

## Build workspace

```bash
cd ~/tb4_project_ab
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Launch simulator

```bash
cd ~/tb4_project_ab
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  model:=lite world:=warehouse x:=2.0 y:=0.0 z:=0.01 yaw:=0.0
```

## Chạy full mission

```bash
cd ~/tb4_project_ab
export ROS_DOMAIN_ID=7
export RMW_FASTRTPS_USE_SHM=0
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch tb4_bringup sim_demo.launch.py use_rviz:=true
```

## Kiểm tra topic quan trọng

```bash
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 topic echo /clock --once
ros2 topic echo /vision/detected_objects --once
ros2 topic echo /target_object_pose_map --once
ros2 topic echo /target_object_marker --once
```

---

# Phụ Lục C: Một Số Lỗi Và Cách Khắc Phục

## Lỗi ROS daemon hoặc session cũ

- Dừng daemon.
- Kill các process cũ.
- Xóa cache shared memory nếu cần.
- Source lại môi trường.

## Lỗi `/scan` toàn `0.164`

- Kiểm tra dữ liệu LiDAR.
- Kiểm tra vị trí RPLIDAR trong URDF/Xacro.
- Kiểm tra collision giữa LiDAR và robot model.
- Điều chỉnh offset RPLIDAR nếu cần.

## Lỗi RViz không thấy map

- Kiểm tra `/map` có publisher không.
- Kiểm tra fixed frame là `map`.
- Kiểm tra SLAM hoặc map server đã chạy chưa.
- Kiểm tra robot có di chuyển đủ để SLAM mở rộng map chưa.

## Lỗi không thấy target marker

- Kiểm tra YOLO có publish `/vision/detected_objects` không.
- Kiểm tra depth topic có dữ liệu không.
- Kiểm tra `/target_object_pose_map` có dữ liệu không.
- Trong RViz thêm display `Marker` với topic `/target_object_marker`.
