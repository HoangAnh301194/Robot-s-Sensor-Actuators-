# TurtleBot4 Real-Robot Run Checklist

## 1. Network and ROS discovery

Use one discovery mode only. Do not mix Simple Discovery and Discovery Server.

### Simple Discovery

On both PC and TurtleBot4:

```bash
export ROS_DOMAIN_ID=<same_domain_as_robot>
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_DISCOVERY_SERVER
ros2 daemon stop
ros2 daemon start
```

### Discovery Server

On PC:

```bash
export ROS_DOMAIN_ID=<same_domain_as_robot>
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DISCOVERY_SERVER=<robot_ip>:11811
ros2 daemon stop
ros2 daemon start
```

Then verify:

```bash
ros2 topic list
ros2 node list
ros2 topic echo /scan --once
ros2 topic echo /odom --once
```

## 2. Check real sensor topics

Before launching perception, verify real OAK-D topic names:

```bash
ros2 topic list | grep -i oak
ros2 topic list | grep -i image
ros2 topic list | grep -i depth
ros2 topic list | grep -i camera_info
```

If names differ, override launch args:

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py \
  map:=~/maps/tb4_lab.yaml \
  image_topic:=/your/rgb/topic \
  depth_topic:=/your/depth/topic \
  camera_info_topic:=/your/camera_info/topic \
  camera_frame:=<camera_frame_if_real_frame_differs> \
  use_rviz:=true
```

## 3. Build workspace

```bash
cd ~/tb4_project_ab
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Python dependencies required by vision/localization:

```bash
pip install ultralytics opencv-python numpy
```

## 4. Create or load map

Mapping on real robot:

```bash
ros2 launch tb4_bringup slam_demo.launch.py use_sim_time:=false use_rviz:=true
```

Drive with teleop, then save:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/maps/tb4_lab
```

## 5. Edit patrol waypoints

Default file:

```text
tb4_nav_patrol/config/patrol_waypoints.yaml
```

For real robot, keep first test waypoints close, slow, and obstacle-free. You can pass a custom installed YAML:

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py \
  map:=~/maps/tb4_lab.yaml \
  waypoints_file:=/absolute/path/to/patrol_waypoints.yaml \
  patrol_start_delay:=60.0 \
  use_rviz:=true
```

## 6. Run real mission safely

```bash
ros2 launch tb4_bringup real_robot_demo.launch.py \
  map:=~/maps/tb4_lab.yaml \
  use_sim_time:=false \
  use_rviz:=true \
  patrol_start_delay:=60.0
```

During delay, set initial pose in RViz with `2D Pose Estimate`.

Check:

```bash
ros2 action list | grep navigate_to_pose
ros2 topic echo /vision/detected_objects --once
ros2 topic echo /target_object_pose_map --once
```

## 7. Safety notes

- Keep robot on blocks or with wheels lifted for first `/cmd_vel` test.
- Keep emergency stop accessible.
- Start with short waypoints in open space.
- Test Nav2 alone before enabling mission manager/perception.
- Use `patrol_start_enabled:=false` if you only want to bring up perception/Nav2 first.
