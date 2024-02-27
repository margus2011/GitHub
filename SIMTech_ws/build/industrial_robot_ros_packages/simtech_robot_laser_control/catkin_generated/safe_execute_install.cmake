execute_process(COMMAND "/home/jeeva/GitHub/SIMTech_ws/build/industrial_robot_ros_packages/simtech_robot_laser_control/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/jeeva/GitHub/SIMTech_ws/build/industrial_robot_ros_packages/simtech_robot_laser_control/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
