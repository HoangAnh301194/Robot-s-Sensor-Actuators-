# tb4_object_localization - 3D Object Localization

## Mô tả module

Module này chịu trách nhiệm:
- Xử lý depth data từ OAK-D-Lite
- Ước lượng vị trí 3D của vật thể
- Chuyển đổi tọa độ giữa các frame (camera → base_link → map)
- Quản lý TF (Transform Framework)

## Cấu trúc thư mục

```
tb4_object_localization/
├── launch/          # Launch files
├── config/          # TF config, frame definitions
├── scripts/         # Localization & TF conversion scripts
└── README.md        # Tài liệu module
```

## Thành viên chịu trách nhiệm

- **Member 3**: Depth processing & 3D localization + TF

## Công việc cần làm

- [ ] Xử lý depth data từ detection
- [ ] Ước lượng vị trí 3D vật thể
- [ ] Chuyển đổi coordinate frame
- [ ] Publish TF transforms
- [ ] Test coordinate transformations

## Tài liệu

- [ROS 2 TF2 Documentation](https://docs.ros.org/en/humble/Concepts/Intermediate/Tf2/index.html)
- [Depth Processing](https://learnopencv.com/)
