# Điều hướng robot di động dựa trên thị giác với mô hình AI tối ưu hóa cho thiết bị biên trên TurtleBot 4 Lite

## 1. Tổng quan dự án

Dự án này xây dựng một hệ thống điều hướng robot di động dựa trên thị giác cho **TurtleBot 4 Lite**.

Robot sẽ tuần tra trong một bản đồ đã biết bằng **ROS 2 Navigation2 (Nav2)**. Trong quá trình tuần tra, robot sử dụng camera **OAK-D-Lite RGB-D** để phát hiện vật thể mục tiêu bằng một mô hình object detection nhẹ, được tối ưu cho thiết bị biên. Khi phát hiện vật thể, hệ thống sử dụng thông tin depth để ước lượng vị trí 3D của vật thể, chuyển vị trí đó sang hệ tọa độ của robot/bản đồ, sinh một goal an toàn gần vật thể, rồi gửi goal đó cho Nav2. Sau đó robot tự lập kế hoạch đường đi, tránh vật cản, tiến gần tới mục tiêu và dừng ở khoảng cách an toàn.

Tên đề tài tiếng Việt:

```text
Điều hướng robot di động dựa trên thị giác với mô hình AI tối ưu hóa cho thiết bị biên trên TurtleBot 4 Lite
```

Tên đề tài tiếng Anh:

```text
Edge-Optimized Vision-Guided Navigation for Object Search on TurtleBot 4 Lite
```

---

## 2. Ý tưởng bài toán

Bài toán chính của dự án là:

> Làm thế nào để một robot di động sử dụng thị giác và thông tin chiều sâu để tìm kiếm vật thể mục tiêu, ước lượng vị trí 3D của vật thể, sau đó tự điều hướng tới một vị trí an toàn gần vật thể đó?

Hành vi mong muốn của robot:

```text
1. Dùng Nav2 để di chuyển tuần tra trong bản đồ đã biết.
2. Dùng OAK-D-Lite để chạy mô hình object detection nhẹ.
3. Khi phát hiện vật thể mục tiêu, dùng depth để ước lượng vị trí 3D tương đối của vật thể.
4. Chuyển vị trí vật thể từ camera frame sang base_link / odom / map frame.
5. Sinh một goal an toàn gần vật thể đã phát hiện.
6. Gửi goal đó cho Nav2.
7. Nav2 tự lập kế hoạch và điều khiển robot tiếp cận mục tiêu.
8. Robot dừng ở một khoảng cách an toàn đã định trước so với vật thể.
```

---

## 3. Triết lý thiết kế của dự án

Repository này là một **ROS 2 repository ở tầng ứng dụng**.

Repository này **không sửa đổi** source code chính thức của TurtleBot 4, mô hình robot, simulator, driver hoặc source code của Nav2.

Các package chính thức của TurtleBot 4 đóng vai trò cung cấp nền tảng robot:

```text
- robot base
- sensor topics
- odometry
- TF tree
- môi trường mô phỏng
- các interface của Nav2
```

Repository này cung cấp phần logic ứng dụng do nhóm tự viết:

```text
- hành vi tuần tra
- object detection
- định vị 3D vật thể
- sinh goal tiếp cận vật thể
- quản lý nhiệm vụ
- bringup toàn hệ thống
```

Logic chính của dự án cần có khả năng chạy được ở cả mô phỏng và robot thật.

Nguyên tắc thiết kế quan trọng:

```text
Simulation và real robot chỉ nên khác nhau ở launch file và file cấu hình.
Các ROS 2 node lõi nên được giữ nguyên.
```

---

## 4. Các giai đoạn phát triển

### Giai đoạn 1 — Mô phỏng

Ở giai đoạn đầu, toàn bộ quá trình phát triển được thực hiện trong mô phỏng.

TurtleBot 4 Lite simulator cung cấp:

```text
- mô hình robot
- cảm biến mô phỏng
- odometry
- TF
- map / localization / Nav2 interfaces
```

Repository của nhóm cung cấp:

```text
- các package ROS 2 tự viết
- logic nhiệm vụ
- pipeline object detection
- pipeline định vị vật thể
- logic sinh goal
```

Trong mô phỏng, toàn bộ hệ thống có thể chạy trên laptop Ubuntu dùng để phát triển.

---

### Giai đoạn 2 — Triển khai trên robot thật

Sau khi pipeline mô phỏng hoạt động ổn định, hệ thống sẽ được triển khai lên TurtleBot 4 Lite thật.

TurtleBot 4 Lite thật cung cấp:

```text
- Create 3 mobile base
- RPLIDAR
- OAK-D-Lite
- odometry
- TF tree
- sensor topics
```

Laptop Ubuntu chạy:

```text
- repository này
- các node ứng dụng do nhóm tự viết
- RViz / công cụ giám sát
- các node điều khiển nhiệm vụ nếu cần
```

Laptop và robot giao tiếp với nhau thông qua mạng ROS 2, sử dụng cùng một `ROS_DOMAIN_ID`.

---

## 5. Pipeline hệ thống

Pipeline đầy đủ của hệ thống:

```text
TurtleBot 4 Lite / Simulator
        |
        v
Nav2 Patrol trong bản đồ đã biết
        |
        v
Camera OAK-D-Lite RGB-D
        |
        v
Object Detection nhẹ
        |
        v
2D Bounding Box + Depth Image
        |
        v
Vị trí 3D của vật thể trong Camera Frame
        |
        v
TF Transform: camera_frame -> base_link -> odom -> map
        |
        v
Sinh goal an toàn gần vật thể
        |
        v
Nav2 NavigateToPose / FollowWaypoints
        |
        v
Robot tiếp cận và dừng gần mục tiêu
```

---

## 6. Kiến trúc tổng quát

```text
+---------------------------------------------------------------+
|                      TurtleBot 4 Platform                     |
|                                                               |
|  /scan   /odom   /tf   /tf_static   RGB image   depth image   |
+---------------------------------------------------------------+
                              |
                              v
+---------------------------------------------------------------+
|                      Project Application Layer                |
|                                                               |
|  tb4_nav_patrol                                               |
|      - waypoint patrol                                        |
|      - interface gửi lệnh cho Nav2                            |
|                                                               |
|  tb4_vision_oak                                               |
|      - nhận ảnh RGB                                           |
|      - object detection                                       |
|      - xuất 2D bounding box                                   |
|                                                               |
|  tb4_object_localization                                      |
|      - bbox + depth + camera info                             |
|      - ước lượng pose 3D của vật thể                           |
|      - TF transform sang map/base_link                        |
|                                                               |
|  tb4_mission_manager                                          |
|      - state machine                                          |
|      - xác nhận object detection                              |
|      - sinh goal an toàn                                      |
|      - điều kiện dừng                                         |
|                                                               |
|  tb4_bringup                                                  |
|      - launch cho simulation                                  |
|      - launch cho robot thật                                  |
|      - cấu hình dùng chung                                    |
+---------------------------------------------------------------+
```

---

## 7. Cấu trúc repository dự kiến

```text
tb4-vision-guided-navigation/
├── README.md
├── .gitignore
├── docs/
│   ├── system_architecture.md
│   ├── setup_simulation.md
│   ├── setup_real_robot.md
│   ├── git_workflow.md
│   └── experiment_log.md
│
├── tb4_nav_patrol/
│   ├── package.xml
│   ├── setup.py
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   └── README.md
│
├── tb4_vision_oak/
│   ├── package.xml
│   ├── setup.py
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   ├── models/
│   └── README.md
│
├── tb4_object_localization/
│   ├── package.xml
│   ├── setup.py
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   └── README.md
│
├── tb4_mission_manager/
│   ├── package.xml
│   ├── setup.py
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   └── README.md
│
└── tb4_bringup/
    ├── package.xml
    ├── setup.py
    ├── launch/
    │   ├── sim_demo.launch.py
    │   └── real_robot_demo.launch.py
    ├── config/
    │   ├── sim.yaml
    │   └── real_robot.yaml
    └── README.md
```

---

## 8. Chia module

### Module 1 — `tb4_nav_patrol`

Trách nhiệm chính:

```text
Làm cho robot tuần tra trong bản đồ đã biết bằng Nav2.
```

Công việc:

```text
- Cài đặt và chạy TurtleBot 4 Lite trong mô phỏng.
- Chạy Nav2 trong môi trường mô phỏng.
- Định nghĩa các waypoint tuần tra.
- Viết hành vi waypoint patrol.
- Gửi navigation goal cho Nav2.
- Theo dõi trạng thái điều hướng.
```

Kết quả mong đợi:

```text
Robot có thể di chuyển qua các điểm tuần tra đã định trước trong mô phỏng.
```

Branch gợi ý:

```text
feature/nav2-patrol
```

---

### Module 2 — `tb4_vision_oak`

Trách nhiệm chính:

```text
Chạy object detection bằng ảnh RGB từ OAK-D-Lite hoặc từ camera topic mô phỏng.
```

Công việc:

```text
- Subscribe RGB image topic.
- Chạy mô hình object detection nhẹ.
- Publish kết quả detection 2D.
- Hiển thị bounding box để debug.
- Chuẩn bị model cho triển khai trên thiết bị biên.
```

Kết quả mong đợi:

```text
Detector publish được class, confidence và 2D bounding box của vật thể.
```

Branch gợi ý:

```text
feature/oakd-detection
```

---

### Module 3 — `tb4_object_localization`

Trách nhiệm chính:

```text
Ước lượng vị trí 3D của vật thể đã phát hiện bằng depth và camera intrinsics.
```

Công việc:

```text
- Subscribe kết quả detection 2D.
- Subscribe depth image.
- Subscribe camera info.
- Ước lượng vị trí 3D của vật thể trong camera frame.
- Chuyển object pose sang base_link / odom / map bằng tf2.
- Publish object pose và RViz marker.
```

Kết quả mong đợi:

```text
Vị trí vật thể có sẵn dưới dạng PoseStamped trong map frame.
```

Branch gợi ý:

```text
feature/object-localization
```

---

### Module 4 — `tb4_mission_manager`

Trách nhiệm chính:

```text
Điều khiển toàn bộ hành vi của robot từ tuần tra tới tiếp cận vật thể.
```

Công việc:

```text
- Quản lý các trạng thái nhiệm vụ.
- Chuyển từ chế độ patrol sang chế độ tiếp cận vật thể.
- Xác nhận vật thể qua nhiều frame liên tiếp.
- Sinh goal điều hướng an toàn gần vật thể.
- Gửi goal cho Nav2.
- Cho robot dừng ở khoảng cách an toàn.
- Cho robot tiếp tục patrol nếu cần.
```

Kết quả mong đợi:

```text
Robot có thể tuần tra, phát hiện vật thể, tiếp cận vật thể và dừng an toàn.
```

Branch gợi ý:

```text
feature/mission-manager
```

---

### Module 5 — `tb4_bringup`

Trách nhiệm chính:

```text
Launch và cấu hình toàn bộ hệ thống.
```

Công việc:

```text
- Cung cấp launch file cho simulation.
- Cung cấp launch file cho robot thật.
- Lưu các file cấu hình dùng chung.
- Kết nối các module lại với nhau.
- Định nghĩa topic name và frame name thông qua YAML file.
```

Kết quả mong đợi:

```text
Toàn bộ project có thể được khởi động bằng một lệnh launch.
```

Branch gợi ý:

```text
feature/bringup
```

---

## 9. ROS 2 Interfaces

Để hệ thống dễ tích hợp, các module cần giao tiếp với nhau thông qua các ROS 2 interface rõ ràng.

### Input Topics từ TurtleBot 4 / Simulator

Tên topic có thể khác nhau giữa mô phỏng và robot thật. Vì vậy, tên topic nên được lưu trong file YAML thay vì hard-code trực tiếp trong source code.

Các input thường cần:

```text
/scan
/odom
/tf
/tf_static
/map
/rgb/image
/depth/image
/camera_info
```

Ví dụ camera topics:

```text
/oakd/rgb/preview/image_raw
/oakd/stereo/image_raw
/oakd/rgb/camera_info
```

---

### Output Topics của project

Các topic cấp project được gợi ý:

```text
/detected_objects_2d
/target_object_pose_camera
/target_object_pose_base_link
/target_object_pose_map
/object_marker
/mission_state
/object_search/status
```

---

### Navigation Actions

Mission manager nên gửi lệnh điều hướng thông qua Nav2 actions:

```text
/navigate_to_pose
/follow_waypoints
```

Dự án nên tránh điều khiển trực tiếp `/cmd_vel` trong quá trình navigation bình thường, vì việc lập kế hoạch đường đi và tránh vật cản nên do Nav2 xử lý.

Việc điều khiển trực tiếp `/cmd_vel` chỉ nên dùng cho test đơn giản hoặc hành vi dừng khẩn cấp.

---

## 10. Hệ tọa độ và TF frames

TF chain mong muốn:

```text
map -> odom -> base_link -> camera_frame
```

Module định vị vật thể trước tiên sẽ ước lượng vị trí vật thể trong camera frame:

```text
camera_frame
```

Sau đó transform sang:

```text
base_link
```

và cuối cùng sang:

```text
map
```

Goal gửi cho Nav2 phải được biểu diễn trong `map` frame.

Quy tắc quan trọng:

```text
Không bao giờ gửi Nav2 goal trong camera_frame hoặc base_link nếu Nav2 đang yêu cầu goal trong map frame.
```

---

## 11. Simulation Mode và Real Robot Mode

### Simulation Mode

Launch file cho mô phỏng:

```bash
ros2 launch tb4_bringup sim_demo.launch.py
```

File cấu hình cho mô phỏng:

```text
tb4_bringup/config/sim.yaml
```

Simulation mode có thể dùng:

```text
- camera topics mô phỏng
- fake object publisher
- fake detection results
- Nav2 mô phỏng
- map mô phỏng
```

---

### Real Robot Mode

Launch file cho robot thật:

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py
```

File cấu hình cho robot thật:

```text
tb4_bringup/config/real_robot.yaml
```

Real robot mode dùng:

```text
- topic camera OAK-D-Lite thật
- depth image thật
- odometry thật
- TF tree thật
- Nav2 thật
```

Logic ứng dụng lõi cần được giữ nguyên.

---

## 12. Cài đặt Python Virtual Environment

### Lý do cần virtual environment

**Lý do:**
- **Tách biệt dependencies**: Dự án này dùng nhiều thư viện Python (OpenCV, YOLOv8, DepthAI, NumPy). Virtual environment giúp cách ly các thư viện này khỏi hệ thống toàn cục, tránh conflict version.
- **Ổn định phiên bản**: Lock version Python 3.10 để đảm bảo tất cả thành viên trong nhóm chạy cùng môi trường.
- **Dễ dàng deploy**: Khi triển khai lên TurtleBot 4 Lite, virtual environment giúp quá trình cài đặt lặp lại được một cách nhất quán.
- **Tránh lỗi permission**: Không cần `sudo` để cài package vào venv cá nhân.

### Bước 0 — Cài đặt Python 3.10 Virtual Environment (Ubuntu)

**Yêu cầu:** Ubuntu 20.04 LTS hoặc mới hơn, Python 3.10 đã được cài đặt.

```bash
# 1. Kiểm tra Python 3.10 đã cài chưa
python3.10 --version

# 2. Cài python3.10-venv nếu chưa cài
sudo apt-get update
sudo apt-get install -y python3.10-venv python3.10-dev

# 3. Tạo virtual environment cho dự án
python3.10 -m venv ~/tb4_project_venv

# 4. Kích hoạt virtual environment
source ~/tb4_project_venv/bin/activate

# 5. Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# 6. Cài dependencies từ requirements.txt
pip install -r requirements.txt
```

**Lưu ý:**
- Mỗi lần mở terminal mới để làm việc, cần chạy: `source ~/tb4_project_venv/bin/activate`
- Khi kích hoạt venv, prompt sẽ hiển thị `(tb4_project_venv)` ở đầu dòng
- Để thoát venv: `deactivate`

---

## 13. Quy trình setup cơ bản

### Bước 1 — Tạo ROS 2 workspace

```bash
mkdir -p ~/tb4_project_ws/src
cd ~/tb4_project_ws/src
```

### Bước 2 — Clone repository này

```bash
git clone https://github.com/<team-name>/tb4-vision-guided-navigation.git
```

### Bước 3 — Cài dependency

```bash
cd ~/tb4_project_ws
rosdep install --from-paths src -y --ignore-src
```

### Bước 4 — Build workspace

```bash
colcon build
```

### Bước 5 — Source workspace

```bash
source install/setup.bash
```

---

## 13. Thiết lập môi trường khuyến nghị

Mỗi terminal nên source ROS 2 và workspace:

```bash
source ~/tb4_project_venv/bin/activate
source /opt/ros/humble/setup.bash
source ~/tb4_project_ws/install/setup.bash
export ROS_DOMAIN_ID=17
```

Có thể tạo script môi trường:

```bash
source scripts/setup_tb4_env.sh
```

Nội dung gợi ý cho `scripts/setup_tb4_env.sh`:

```bash
#!/bin/bash

# Activate Python virtual environment
source ~/tb4_project_venv/bin/activate

source /opt/ros/humble/setup.bash

export ROS_DOMAIN_ID=17
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

if [ -f ~/tb4_project_ws/install/setup.bash ]; then
    source ~/tb4_project_ws/install/setup.bash
fi

echo "Python venv: $(which python)"
echo "ROS_DISTRO=$ROS_DISTRO"
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
```

---

## 14. Chạy hệ thống trong mô phỏng

Terminal 1 — Chạy TurtleBot 4 Lite simulation:

```bash
source ~/tb4_project_venv/bin/activate
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=17
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py model:=lite
```

Terminal 2 — Chạy các node ứng dụng của project:

```bash
cd ~/tb4_project_ws
source install/setup.bash
export ROS_DOMAIN_ID=17
ros2 launch tb4_bringup sim_demo.launch.py
```

Terminal 3 — Debug topic và node:

```bash
ros2 topic list
ros2 node list
ros2 action list
ros2 topic echo /odom
ros2 topic echo /scan
```

---

## 15. Chạy hệ thống trên TurtleBot 4 Lite thật

Trước khi chạy project trên robot thật, cần đảm bảo:

```text
- Robot đã được bật nguồn.
- Laptop và robot đang ở cùng mạng.
- Laptop và robot dùng cùng ROS_DOMAIN_ID.
- Laptop có thể thấy các topic của robot.
- Nav2 đang chạy và sẵn sàng.
- Camera và depth topics đã có.
```

Kiểm tra kết nối với robot:

```bash
source ~/tb4_project_venv/bin/activate
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=17
ros2 topic list
```

Chạy các node ứng dụng của project:

```bash
cd ~/tb4_project_ws
source ~/tb4_project_venv/bin/activate
source install/setup.bash
export ROS_DOMAIN_ID=17
ros2 launch tb4_bringup real_robot_demo.launch.py
```

---

## 17. Mission State Machine

Mission manager nên tuân theo state machine sau:

```text
IDLE
  |
  v
PATROL
  |
  v
OBJECT_DETECTED
  |
  v
OBJECT_CONFIRMED
  |
  v
GENERATE_APPROACH_GOAL
  |
  v
NAVIGATE_TO_OBJECT
  |
  v
STOP_NEAR_OBJECT
  |
  v
REPORT_FOUND
  |
  v
RESUME_PATROL
```

Các trạng thái lỗi có thể có:

```text
OBJECT_LOST
NAVIGATION_FAILED
TF_LOOKUP_FAILED
DEPTH_INVALID
TIMEOUT
EMERGENCY_STOP
```

---

## 17. Sinh goal an toàn

Robot không nên điều hướng thẳng tới tâm của vật thể.

Thay vào đó, robot nên dừng ở một khoảng cách an toàn so với vật thể.

Cho:

```text
vị trí vật thể: (x_obj, y_obj)
vị trí robot:   (x_robot, y_robot)
khoảng cách an toàn: d_safe
```

Goal tiếp cận có thể được sinh theo hướng từ vật thể về robot:

```text
dx = x_robot - x_obj
dy = y_robot - y_obj
norm = sqrt(dx^2 + dy^2)

x_goal = x_obj + d_safe * dx / norm
y_goal = y_obj + d_safe * dy / norm
yaw_goal = atan2(y_obj - y_goal, x_obj - x_goal)
```

Goal này phải được gửi cho Nav2 trong `map` frame.

---

## 18. Git workflow cho thành viên trong nhóm

Mỗi thành viên nên làm việc trên một branch riêng.

### Clone repository

```bash
git clone https://github.com/<team-name>/tb4-vision-guided-navigation.git
cd tb4-vision-guided-navigation
```

### Tạo branch

```bash
git checkout -b feature/module-name
```

Ví dụ:

```bash
git checkout -b feature/nav2-patrol
git checkout -b feature/oakd-detection
git checkout -b feature/object-localization
git checkout -b feature/mission-manager
```

### Commit thay đổi

```bash
git add .
git commit -m "Add short description"
```

### Push branch

```bash
git push origin feature/module-name
```

### Tạo Pull Request

Tạo Pull Request từ:

```text
feature/module-name -> main
```

Ít nhất một thành viên khác nên review Pull Request trước khi merge.

Không push trực tiếp lên `main`.

---

## 19. Quy tắc phát triển

### Không sửa package chính thức của TurtleBot 4

Dự án này không nên chỉnh sửa:

```text
- turtlebot4
- turtlebot4_simulator
- turtlebot4_robot
- turtlebot4_desktop
- nav2 source code
```

Các package chính thức nên được cài bằng apt khi có thể.

---

### Không hard-code tên topic

Sử dụng file cấu hình YAML cho:

```text
- image topic
- depth topic
- camera info topic
- target frame
- robot frame
- safe distance
- detection confidence threshold
```

---

### Không commit thư mục build

Không commit:

```text
build/
install/
log/
```

---

### Không commit model nặng nếu không cần thiết

Các file model dung lượng lớn thường nên được lưu bên ngoài repository.

Ví dụ:

```text
*.pt
*.onnx
*.engine
*.blob
```

Nếu cần, hãy cung cấp link tải trong README của module tương ứng.

---

## 20. `.gitignore` gợi ý

```gitignore
# ROS 2 build folders
build/
install/
log/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/

# Virtual environments
venv/
.env/

# VSCode
.vscode/

# Models and datasets
*.pt
*.onnx
*.engine
*.blob
datasets/
data/

# Logs
*.log

# OS files
.DS_Store
Thumbs.db
```

---

## 21. Kế hoạch tích hợp

### Phase 1 — Mô phỏng cơ bản

Mục tiêu:

```text
TurtleBot 4 Lite chạy được trong mô phỏng và có thể điều hướng bằng Nav2.
```

Module chính:

```text
tb4_nav_patrol
```

---

### Phase 2 — Fake Object Pipeline

Mục tiêu:

```text
Publish một fake object pose trong map frame và làm cho robot điều hướng tới gần nó.
```

Module chính:

```text
tb4_object_localization
tb4_mission_manager
```

---

### Phase 3 — Real Detection Pipeline trong mô phỏng

Mục tiêu:

```text
Dùng output của object detection và thông tin depth để ước lượng vị trí 3D của vật thể.
```

Module chính:

```text
tb4_vision_oak
tb4_object_localization
```

---

### Phase 4 — Full Simulation Demo

Mục tiêu:

```text
Robot tuần tra, phát hiện vật thể, ước lượng vị trí 3D, sinh goal, tiếp cận vật thể và dừng an toàn.
```

Module chính:

```text
all modules
```

---

### Phase 5 — Real Robot Demo

Mục tiêu:

```text
Chạy cùng logic ứng dụng trên TurtleBot 4 Lite thật.
```

Module chính:

```text
all modules
```

---

## 22. Debug checklist

### Kiểm tra môi trường ROS 2

```bash
echo $ROS_DISTRO
echo $ROS_DOMAIN_ID
echo $RMW_IMPLEMENTATION
```

### Kiểm tra node đang chạy

```bash
ros2 node list
```

### Kiểm tra topic đang có

```bash
ros2 topic list
```

### Kiểm tra Nav2 actions

```bash
ros2 action list
```

Các action mong đợi có thể gồm:

```text
/navigate_to_pose
/follow_waypoints
```

### Kiểm tra TF tree

```bash
ros2 run tf2_tools view_frames
```

### Kiểm tra odometry của robot

```bash
ros2 topic echo /odom
```

### Kiểm tra lidar

```bash
ros2 topic echo /scan
```

### Kiểm tra camera topics

```bash
ros2 topic list | grep image
ros2 topic list | grep camera
```

---

## 23. Kết quả kì vọng khi Demo cuối kỳ 

Demo cuối cùng cần thể hiện được:

```text
1. TurtleBot 4 Lite khởi động trong một bản đồ đã biết.
2. Robot tuần tra qua các waypoint đã định nghĩa.
3. Robot phát hiện vật thể mục tiêu bằng camera.
4. Vật thể được hiển thị bằng bounding box.
5. Vị trí 3D của vật thể được ước lượng bằng depth.
6. Object pose được transform sang map frame.
7. Một goal tiếp cận an toàn được sinh gần vật thể.
8. Nav2 lập kế hoạch và thực thi đường đi.
9. Robot dừng ở khoảng cách an toàn so với vật thể.
10. Mission state được hiển thị hoặc ghi log.
```

---

## 24. Ghi chú cho thành viên nhóm

Trước khi bắt đầu phát triển, mỗi thành viên cần hiểu rõ:

```text
- Module của mình nhận input gì.
- Module của mình publish output gì.
- Những ROS 2 topics/actions/services nào được sử dụng.
- Dữ liệu của mình đang thuộc coordinate frame nào.
- Node của mình đang chạy ở simulation mode hay real robot mode.
- Cách launch và test module độc lập.
```

Mỗi module nên có `README.md` riêng, giải thích:

```text
- mục đích module
- input topics
- output topics
- parameters
- launch commands
- test commands
- lỗi thường gặp
```

---

## 25. Trạng thái hiện tại

```text
Dự án đang ở giai đoạn lập kế hoạch.
Cấu trúc repository và trách nhiệm từng module đang được xác định.
Simulation sẽ được triển khai trước.
Real robot deployment sẽ được thực hiện sau khi pipeline mô phỏng ổn định.


- Member 1: Nav2 Patrol and Simulation
- Member 2: OAK-D-Lite and Object Detection
- Member 3: Depth-based 3D Object Localization
- Member 4: Mission Manager and Integration
```
