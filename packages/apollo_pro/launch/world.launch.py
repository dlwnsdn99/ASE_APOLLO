# Gazebo를 실행시킨 상태에서
# $ ros2 run image_view image_view --ros-args --remap /image:=/diffbot/camera_sensor/image_raw
# 카메라임

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    rviz_file = "diffbot.rviz"  # 3D 파일 명 수정
    robot_file = "diffbot.urdf"  # robot 파일 명 수정
    package_name = "apollo_pro"  # 전체 파일 상위 패키지 명 수정
    world_file_name = "maze_world.world"  # 맵 파일 명 수정

    world = os.path.join(
        get_package_share_directory(package_name), "worlds", world_file_name
    ) #변수 world의 값이 apollo_pro/worlds/maze_world.world
    urdf_file = os.path.join(get_package_share_directory(package_name), "urdf", robot_file) #로봇 파일
    rviz_config = os.path.join(get_package_share_directory(package_name), "rviz", rviz_file) #rviz툴

    robot_desc = open(urdf_file, "r").read()

    xml = robot_desc.replace('"', '\\"')

    orientation = "{ orientation : { x : 0.0, y: 0.0, z: 0.707, w: 0.707 } }"

    spwan_args = '{name: "diffbot", xml: "' + xml + '", initial_pose :' + orientation + '}'

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
        arguments=[urdf_file],
    )

    return LaunchDescription(  # 실행시킬 Node를 기술해둔 Description
        [
            robot_state_publisher_node,
            ExecuteProcess(  # gazebo 실행
                cmd=["gazebo", "--verbose", world, "-s", "libgazebo_ros_factory.so"],
                output="screen",
            ),
            ExecuteProcess(  # robot 동작
                cmd=["ros2", "service", "call", "/spawn_entity", "gazebo_msgs/SpawnEntity", spwan_args],
                output="screen",
            ),
            ExecuteProcess(  # rviz 실행
                cmd=["ros2", "run", "rviz2", "rviz2", "-d", rviz_config],
                output="screen"
            ),
        ]
    )