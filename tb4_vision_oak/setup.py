import os
from glob import glob

from setuptools import find_packages, setup

package_name = "tb4_vision_oak"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test", "scripts"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # Copy toàn bộ file launch vào thư mục cài đặt
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*")),
        # Copy thư mục models vào thư mục cài đặt
        (os.path.join("share", package_name, "models"), glob("models/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="nhatnguyen",
    maintainer_email="nhatnguyen@todo.todo",
    description="OAK-D Lite Object Detection for TurtleBot 4",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "detection_node = tb4_vision_oak.detection_node:main"
        ],
    },
)
