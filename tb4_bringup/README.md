# tb4_bringup - System Bringup

## Mô tả module

Module này chịu trách nhiệm:
- Khởi động toàn hộ hệ thống
- Cung cấp launch file chung cho simulation
- Cung cấp launch file chung cho real robot

## Cấu trúc thư mục

```
tb4_bringup/
├── launch/
│   ├── sim_demo.launch.py       # Launch toàn hệ thống trên simulation
│   └── real_robot_demo.launch.py # Launch toàn hệ thống trên real robot
└── config/
```

## Cách sử dụng

### Mô phỏng (Simulation)
```bash
ros2 launch tb4_bringup sim_demo.launch.py
```

### Robot thật
```bash
ros2 launch tb4_bringup real_robot_demo.launch.py
```

## Thành viên chịu trách nhiệm

- **Tất cả thành viên**: Cùng tham gia tạo bringup

## Công việc cần làm

- [ ] Tạo master launch file cho simulation
- [ ] Tạo master launch file cho real robot
- [ ] Cấu hình parameters chung
- [ ] Test tất cả modules hoạt động cùng nhau
