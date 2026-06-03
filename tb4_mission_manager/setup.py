from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'tb4_mission_manager'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=["test", "scripts"]),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hoang_anh',
    maintainer_email='hoang_anh@todo.todo',
    description='Mission management for TurtleBot 4 Lite',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'mission_manager_node = tb4_mission_manager.mission_manager_node:main'
        ],
    },
)
