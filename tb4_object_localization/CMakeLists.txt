cmake_minimum_required(VERSION 3.8)
project(tb4_object_localization)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Khai báo cài đặt file code Python trong thư mục scripts
install(PROGRAMS
  scripts/localization_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# Khai báo cài đặt thư mục launch (nếu sau này bạn dùng)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
