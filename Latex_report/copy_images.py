import shutil
import os

src_dir = "/home/hoang_anh/.gemini/antigravity/brain/ff608847-5ef4-4006-acb4-0c735e4cd634"

files = [
    ("rqt_graph_1780577164853.png", "images/chapter3/rqt_graph.png"),
    ("yolo_detection_1780577152414.png", "images/chapter4/yolo_detection.png"),
    ("rviz_nav2_1780577141225.png", "images/chapter6/rviz_nav2.png")
]

for src_name, dst_path in files:
    src = os.path.join(src_dir, src_name)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy(src, dst_path)
    print(f"Copied {src} to {dst_path}")
