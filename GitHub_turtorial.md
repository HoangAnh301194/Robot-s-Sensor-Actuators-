# Git Workflow Guide for TurtleBot 4 Lite Vision-Guided Navigation Project

## 1. Mục tiêu của tài liệu

Tài liệu này hướng dẫn cách sử dụng Git và GitHub cho dự án:

```text
Edge-Optimized Vision-Guided Navigation for Object Search on TurtleBot 4 Lite
```

Dự án được chia thành nhiều module để 4 thành viên có thể làm song song mà không đè code của nhau.

Mục tiêu của workflow Git trong dự án này:

- Mỗi người làm việc trên một branch riêng.
- Không push trực tiếp vào `main`.
- Code xong thì tạo Pull Request.
- Nhóm review trước khi merge vào `main`.
- Dễ theo dõi lịch sử thay đổi của từng module.
- Giảm lỗi conflict khi nhiều người cùng code.

---

## 2. Cấu trúc repo đề xuất

Tên repo gợi ý:

```text
tb4-vision-guided-navigation
```

Cấu trúc thư mục chính:

```text
tb4-vision-guided-navigation/
├── README.md
├── README_GIT_WORKFLOW.md
├── docs/
│   ├── system_architecture.md
│   ├── setup_simulation.md
│   ├── setup_nav2.md
│   ├── setup_oakd.md
│   └── experiment_log.md
│
├── tb4_nav_patrol/              # Module 1: Nav2 patrol + simulation
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   └── README.md
│
├── tb4_vision_oak/              # Module 2: OAK-D-Lite + object detection
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   ├── models/
│   └── README.md
│
├── tb4_object_localization/     # Module 3: depth + 3D localization + TF
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   └── README.md
│
├── tb4_mission_manager/         # Module 4: goal generation + state machine
│   ├── launch/
│   ├── config/
│   ├── scripts/
│   └── README.md
│
└── tb4_bringup/                 # Launch toàn hệ thống
    ├── launch/
    │   ├── sim_demo.launch.py
    │   └── real_robot_demo.launch.py
    └── config/
```

---

## 3. Phân chia branch cho từng thành viên

Mỗi thành viên nên làm trên một branch riêng.

| Thành viên | Module | Branch đề xuất |
|---|---|---|
| Member 1 | Nav2 patrol + simulation | `feature/nav2-patrol` |
| Member 2 | OAK-D-Lite + object detection | `feature/oakd-detection` |
| Member 3 | Depth + 3D object localization + TF | `feature/object-localization` |
| Member 4 | Mission manager + goal generation | `feature/mission-manager` |

Ngoài ra có thể dùng thêm các loại branch sau:

```text
feature/<ten-chuc-nang>     # Thêm chức năng mới
fix/<ten-loi>               # Sửa lỗi
docs/<ten-tai-lieu>         # Viết hoặc sửa tài liệu
test/<ten-test>             # Thêm test hoặc demo
```

Ví dụ:

```text
feature/fake-object-publisher
fix/tf-transform-error
docs/setup-simulation
test/nav2-safe-goal
```

---

## 4. Cài Git lần đầu

Kiểm tra Git đã được cài chưa:

```bash
git --version
```

Nếu chưa có Git trên Ubuntu:

```bash
sudo apt update
sudo apt install git -y
```

Cấu hình tên và email:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Kiểm tra cấu hình:

```bash
git config --global --list
```

---

## 5. Clone repo về máy

Sau khi repo được tạo trên GitHub, mỗi thành viên clone repo về máy:

```bash
git clone https://github.com/<owner>/tb4-vision-guided-navigation.git
cd tb4-vision-guided-navigation
```

Ví dụ:

```bash
git clone https://github.com/your-team/tb4-vision-guided-navigation.git
cd tb4-vision-guided-navigation
```

Kiểm tra branch hiện tại:

```bash
git branch
```

Thông thường sau khi clone, branch mặc định là:

```text
main
```

---

## 6. Không làm trực tiếp trên `main`

Quy tắc quan trọng:

```text
Không code trực tiếp trên branch main.
```

Branch `main` chỉ chứa code đã ổn định sau khi được review và merge.

Trước khi bắt đầu code, mỗi người cần tạo branch riêng.

---

## 7. Tạo branch làm việc riêng

Ví dụ người phụ trách Nav2 patrol:

```bash
git checkout -b feature/nav2-patrol
```

Người phụ trách OAK-D-Lite detection:

```bash
git checkout -b feature/oakd-detection
```

Người phụ trách object localization:

```bash
git checkout -b feature/object-localization
```

Người phụ trách mission manager:

```bash
git checkout -b feature/mission-manager
```

Kiểm tra đang ở branch nào:

```bash
git branch
```

Branch hiện tại sẽ có dấu `*` phía trước.

Ví dụ:

```text
  main
* feature/nav2-patrol
```

---

## 8. Quy trình làm việc hằng ngày

Mỗi lần bắt đầu làm việc, nên cập nhật code mới nhất từ `main` trước.

### Bước 1: Chuyển về branch `main`

```bash
git checkout main
```

### Bước 2: Kéo code mới nhất từ GitHub

```bash
git pull origin main
```

### Bước 3: Chuyển lại branch cá nhân

```bash
git checkout feature/nav2-patrol
```

Thay `feature/nav2-patrol` bằng branch của mình.

### Bước 4: Merge code mới từ `main` vào branch cá nhân

```bash
git merge main
```

Sau đó mới bắt đầu code tiếp.

---

## 9. Thêm file mới hoặc sửa code

Sau khi code xong, kiểm tra trạng thái repo:

```bash
git status
```

Git sẽ hiển thị các file đã thay đổi.

Ví dụ:

```text
modified:   tb4_nav_patrol/scripts/patrol_node.py
new file:   tb4_nav_patrol/launch/patrol.launch.py
```

---

## 10. Add file vào staging area

Thêm toàn bộ file đã thay đổi:

```bash
git add .
```

Hoặc chỉ thêm một file cụ thể:

```bash
git add tb4_nav_patrol/scripts/patrol_node.py
```

Kiểm tra lại:

```bash
git status
```

---

## 11. Commit thay đổi

Commit là thao tác lưu lại một mốc thay đổi trong Git.

Cú pháp:

```bash
git commit -m "Short description of change"
```

Ví dụ:

```bash
git commit -m "Add Nav2 waypoint patrol node"
```

Một số ví dụ commit message tốt:

```text
Add Nav2 patrol launch file
Add fake object pose publisher
Fix object pose transform to map frame
Update OAK-D detector config
Add mission state machine
Update simulation setup guide
```

Không nên commit message kiểu:

```text
update
fix
abc
code moi
lan 1
```

---

## 12. Push branch lên GitHub

Lần đầu push branch mới:

```bash
git push -u origin feature/nav2-patrol
```

Các lần sau chỉ cần:

```bash
git push
```

Với branch khác, thay tên branch tương ứng:

```bash
git push -u origin feature/oakd-detection
```

---

## 13. Tạo Pull Request trên GitHub

Sau khi push branch, vào trang GitHub của repo.

GitHub thường sẽ hiện nút:

```text
Compare & pull request
```

Chọn:

```text
base: main
compare: feature/your-branch-name
```

Ví dụ:

```text
base: main
compare: feature/nav2-patrol
```

Nội dung Pull Request nên ghi rõ:

```markdown
## What does this PR do?

- Add Nav2 waypoint patrol node.
- Add patrol launch file.
- Add waypoint configuration file.

## How to test?

```bash
ros2 launch tb4_nav_patrol patrol.launch.py
```

## Notes

- Current waypoints are tested in simulation only.
- Need integration with mission manager later.
```

---

## 14. Review và merge Pull Request

Trước khi merge, ít nhất một thành viên khác nên review.

Cần kiểm tra:

- Code có chạy được không?
- Có sửa nhầm file của module khác không?
- Có commit file nặng không?
- Có commit thư mục `build/`, `install/`, `log/` không?
- Có README hoặc hướng dẫn chạy chưa?
- Tên topic, frame, message type có khớp với interface chung không?

Sau khi ổn, merge Pull Request vào `main`.

---

## 15. Sau khi Pull Request được merge

Sau khi branch của mình đã được merge vào `main`, cần cập nhật lại máy local.

```bash
git checkout main
git pull origin main
```

Nếu muốn xóa branch local cũ:

```bash
git branch -d feature/nav2-patrol
```

Nếu muốn xóa branch remote trên GitHub:

```bash
git push origin --delete feature/nav2-patrol
```

Sau đó nếu làm chức năng mới, tạo branch mới từ `main` mới nhất:

```bash
git checkout -b feature/new-feature-name
```

---

## 16. Cập nhật branch cá nhân khi `main` đã thay đổi

Trong lúc mình đang làm, người khác có thể đã merge code mới vào `main`.

Khi đó cần cập nhật branch cá nhân.

Ví dụ đang ở branch:

```text
feature/object-localization
```

Làm như sau:

```bash
git checkout main
git pull origin main
git checkout feature/object-localization
git merge main
```

Nếu không có conflict, Git sẽ merge tự động.

Nếu có conflict, xem mục xử lý conflict bên dưới.

---

## 17. Xử lý conflict cơ bản

Conflict xảy ra khi hai người sửa cùng một vùng trong cùng một file.

Ví dụ Git báo:

```text
CONFLICT (content): Merge conflict in tb4_bringup/launch/sim_demo.launch.py
```

Mở file bị conflict, sẽ thấy dạng:

```text
<<<<<<< HEAD
code của branch hiện tại
=======
code từ branch đang merge vào
>>>>>>> main
```

Cần sửa thủ công để giữ lại phần đúng.

Sau khi sửa xong, xóa các dòng:

```text
<<<<<<< HEAD
=======
>>>>>>> main
```

Sau đó:

```bash
git add tb4_bringup/launch/sim_demo.launch.py
git commit -m "Resolve merge conflict in sim demo launch"
```

Kiểm tra lại:

```bash
git status
```

---

## 18. Quy tắc tránh conflict

Để giảm conflict, nhóm nên tuân thủ các quy tắc sau:

1. Mỗi người chủ yếu sửa trong thư mục module của mình.
2. Trước khi sửa file chung như `tb4_bringup/launch/sim_demo.launch.py`, cần báo trước cho nhóm.
3. Luôn `git pull origin main` trước khi bắt đầu làm việc.
4. Pull Request nên nhỏ, không gom quá nhiều thay đổi trong một PR.
5. Không format lại toàn bộ file nếu chỉ sửa một đoạn nhỏ.
6. Không đổi tên file/thư mục chung nếu chưa thống nhất.

---

## 19. File không nên commit

Không nên commit các thư mục sinh ra khi build ROS 2:

```text
build/
install/
log/
```

Không nên commit file model nặng:

```text
*.pt
*.onnx
*.engine
*.blob
```

Không nên commit dataset lớn:

```text
datasets/
data/
```

Không nên commit cache Python:

```text
__pycache__/
*.pyc
```

---

## 20. File `.gitignore` đề xuất

Tạo file `.gitignore` ở thư mục root của repo:

```gitignore
# ROS 2 build folders
build/
install/
log/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/

# Virtual environments
venv/
.env/
.venv/

# VSCode
.vscode/

# Models and datasets
*.pt
*.onnx
*.engine
*.blob
*.tflite
datasets/
data/

# Logs
*.log

# OS files
.DS_Store
Thumbs.db
```

Nếu cần chia sẻ model, nên dùng một trong các cách sau:

- Google Drive
- GitHub Release
- Hugging Face Model Hub
- Link tải trong README

---

## 21. Một số lệnh Git thường dùng

Kiểm tra trạng thái:

```bash
git status
```

Xem branch hiện tại:

```bash
git branch
```

Xem toàn bộ branch local và remote:

```bash
git branch -a
```

Chuyển branch:

```bash
git checkout branch-name
```

Tạo branch mới:

```bash
git checkout -b branch-name
```

Add toàn bộ thay đổi:

```bash
git add .
```

Commit:

```bash
git commit -m "Commit message"
```

Push:

```bash
git push
```

Pull:

```bash
git pull origin main
```

Xem lịch sử commit:

```bash
git log --oneline --graph --all
```

Xem nội dung thay đổi trước khi commit:

```bash
git diff
```

---

## 22. Workflow mẫu cho từng thành viên

### Lần đầu làm việc

```bash
git clone https://github.com/<owner>/tb4-vision-guided-navigation.git
cd tb4-vision-guided-navigation
git checkout -b feature/nav2-patrol
```

Code trong module của mình.

```bash
git status
git add .
git commit -m "Add Nav2 patrol module structure"
git push -u origin feature/nav2-patrol
```

Sau đó tạo Pull Request trên GitHub.

---

### Mỗi ngày trước khi code

```bash
git checkout main
git pull origin main
git checkout feature/your-branch-name
git merge main
```

Sau đó mới tiếp tục code.

---

### Sau khi code xong trong ngày

```bash
git status
git add .
git commit -m "Describe what you changed"
git push
```

---

## 23. Quy tắc đặt tên topic/interface chung

Để các module dễ ghép với nhau, cần thống nhất interface.

### Object detection output

```text
/detected_objects_2d
```

Message type đề xuất:

```text
vision_msgs/Detection2DArray
```

### Object pose in map frame

```text
/target_object_pose_map
```

Message type đề xuất:

```text
geometry_msgs/PoseStamped
```

### Mission state

```text
/mission_state
```

Message type đề xuất:

```text
std_msgs/String
```

Các trạng thái đề xuất:

```text
PATROL
OBJECT_DETECTED
OBJECT_CONFIRMED
GENERATE_GOAL
NAVIGATE_TO_OBJECT
STOP_NEAR_OBJECT
RESUME_PATROL
```

---

## 24. Quy tắc khi sửa file chung

Các file sau được xem là file chung:

```text
README.md
README_GIT_WORKFLOW.md
tb4_bringup/launch/sim_demo.launch.py
tb4_bringup/launch/real_robot_demo.launch.py
tb4_bringup/config/sim.yaml
tb4_bringup/config/real_robot.yaml
```

Trước khi sửa file chung, nên báo trong nhóm:

```text
Mình đang sửa tb4_bringup/launch/sim_demo.launch.py để ghép Nav2 + mission manager.
```

Sau khi sửa xong, nên tạo Pull Request riêng, không gộp quá nhiều thay đổi module cá nhân vào file chung.

---

## 25. Quy tắc commit cho ROS 2 project

Nên commit những thứ sau:

```text
launch files
config files
source code
README files
small test scripts
small sample configs
```

Không nên commit:

```text
build/
install/
log/
large datasets
large trained models
temporary debug files
```

Trước khi commit, nên chạy:

```bash
git status
```

Nếu thấy `build/`, `install/`, `log/` xuất hiện thì cần kiểm tra lại `.gitignore`.

---

## 26. Pull Request template đề xuất

Có thể tạo file:

```text
.github/pull_request_template.md
```

Nội dung:

```markdown
## Summary

Describe what this Pull Request changes.

## Module

- [ ] Nav2 patrol
- [ ] OAK-D detection
- [ ] Object localization
- [ ] Mission manager
- [ ] Bringup / integration
- [ ] Documentation

## Changes

- 
- 
- 

## How to test

```bash
# Add test command here
```

## Checklist

- [ ] Code runs locally.
- [ ] No `build/`, `install/`, or `log/` folder is committed.
- [ ] No large model or dataset file is committed.
- [ ] README or documentation is updated if needed.
- [ ] Topic names and frame names match the project interface.
```

---

## 27. Recommended team workflow summary

Quy trình chuẩn của nhóm:

```text
clone repo
    ↓
create feature branch
    ↓
work inside assigned module
    ↓
git add + commit
    ↓
git push branch
    ↓
create Pull Request
    ↓
team review
    ↓
merge into main
    ↓
update local main
```

Không push trực tiếp vào `main`.

Mọi thay đổi quan trọng nên đi qua Pull Request.

---

## 28. Ví dụ workflow hoàn chỉnh cho Member 3

Member 3 phụ trách object localization.

```bash
git clone https://github.com/<owner>/tb4-vision-guided-navigation.git
cd tb4-vision-guided-navigation
```

Tạo branch:

```bash
git checkout -b feature/object-localization
```

Tạo file code:

```text
tb4_object_localization/scripts/object_3d_node.py
tb4_object_localization/launch/object_localization.launch.py
tb4_object_localization/config/object_filter.yaml
```

Commit:

```bash
git add tb4_object_localization/
git commit -m "Add depth-based object localization node"
```

Push:

```bash
git push -u origin feature/object-localization
```

Tạo Pull Request:

```text
feature/object-localization → main
```

Sau khi được review, merge vào `main`.

---

## 29. Kết luận

Workflow Git của dự án này nên dựa trên nguyên tắc:

```text
main ổn định
feature branch để phát triển
Pull Request để review
merge sau khi kiểm tra
```

Cách làm này giúp nhóm 4 người phát triển song song các module Nav2, OAK-D detection, object localization và mission manager mà vẫn giữ được repo sạch, dễ debug và dễ tích hợp.
