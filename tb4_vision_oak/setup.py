import os
from glob import glob

from setuptools import find_packages, setup

package_name = "tb4_vision_oak"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # Copy toÃ n bá»™ file launch vÃ o thÆ° má»¥c cÃ i Ä'áº·t
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        # CHá»– Sá»¬A Lá»–I: Copy file script vÃ o thÆ° má»¥c lib Ä'Æ°á»£c ROS 2 cÃ³ thá»ƒ cháº¡y Ä'Æ°á»£c
        (os.path.join("lib", package_name), glob("scripts/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="nhatnguyen",
    maintainer_email="nhatnguyen@todo.todo",
    description="OAK-D Lite Object Detection for TurtleBot 4",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "detection_node = scripts.detection_node:main"
        ],
    },
)
