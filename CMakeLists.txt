cmake_minimum_required(VERSION 3.8)
project(param_configuration)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

install(DIRECTORY
  examples
  DESTINATION share/${PROJECT_NAME}/
)

# find dependencies
find_package(ament_cmake REQUIRED)

### Python support ###
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)

# Install Python modules
ament_python_install_package(${PROJECT_NAME})
# Install Python executables
install(PROGRAMS
  DESTINATION lib/${PROJECT_NAME}
)


# Install global visible executables
install(PROGRAMS
  param_configuration/scripts/config
  DESTINATION bin/
)

if(BUILD_TESTING)
    find_package(ament_cmake_pytest REQUIRED)
    ament_add_pytest_test(${PROJECT_NAME}_test_param_configuration .)
endif()

ament_package()
