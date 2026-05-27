# tb4_mission_manager - Mission Management & Goal Generation

## Mô tả module

Module này chịu trách nhiệm:
- Sinh goal tiếp cận an toàn dựa vào vị trí vật thể
- Quản lý trạng thái hệ thống (state machine)
- Gửi goal cho Nav2
- Xử lý feedback từ các module khác

## Cấu trúc thư mục

```
tb4_mission_manager/
├── launch/          # Launch files
├── config/          # Goal generation parameters
├── scripts/         # State machine & goal generation logic
└── README.md        # Tài liệu module
```

## Thành viên chịu trách nhiệm

- **Member 4**: Mission manager & goal generation

## Công việc cần làm

- [ ] Thiết kế state machine
- [ ] Viết goal generation logic
- [ ] Tích hợp callbacks từ các module
- [ ] Gửi goal đến Nav2
- [ ] Xử lý feedback & error handling

## Tài liệu

- [Nav2 Goal API](https://docs.nav2.org/)
- [ROS 2 Action](https://docs.ros.org/en/humble/Concepts/Intermediate/Actions.html)
