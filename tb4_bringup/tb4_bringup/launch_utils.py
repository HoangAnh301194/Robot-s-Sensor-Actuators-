#!/usr/bin/env python3

import os

from ament_index_python.packages import PackageNotFoundError, get_package_share_directory


def _resolve_first_existing_path(candidates):
    for package_name, relative_parts in candidates:
        try:
            package_share = get_package_share_directory(package_name)
        except PackageNotFoundError:
            continue

        candidate_path = os.path.join(package_share, *relative_parts)
        if os.path.exists(candidate_path):
            return candidate_path

    raise FileNotFoundError(
        "Không tìm thấy file cấu hình mặc định phù hợp trong các package đã cài."
    )


def resolve_default_map():
    return _resolve_first_existing_path(
        [
            ("turtlebot4_navigation", ("maps", "depot.yaml")),
            ("nav2_bringup", ("maps", "turtlebot3_world.yaml")),
        ]
    )


def resolve_default_nav2_params():
    return _resolve_first_existing_path(
        [
            ("turtlebot4_navigation", ("config", "nav2.yaml")),
            ("nav2_bringup", ("params", "nav2_params.yaml")),
        ]
    )


def resolve_default_rviz_config():
    return _resolve_first_existing_path(
        [
            ("tb4_bringup", ("rviz", "tb4_debug.rviz")),
            ("nav2_bringup", ("rviz", "nav2_default_view.rviz")),
        ]
    )


def resolve_default_slam_params():
    return _resolve_first_existing_path(
        [
            ("tb4_bringup", ("config", "slam_toolbox_tb4.yaml")),
            ("slam_toolbox", ("config", "mapper_params_online_async.yaml")),
        ]
    )
