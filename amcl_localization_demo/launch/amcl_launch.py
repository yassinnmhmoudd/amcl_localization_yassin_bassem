import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    amcl_demo_dir = get_package_share_directory('amcl_localization_demo')
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

    amcl_params = os.path.join(amcl_demo_dir, 'config', 'amcl.yaml')
    map_yaml_path = os.path.join(amcl_demo_dir, 'map', 'turtlebot3_world_map.yaml')

    # Launch turtlebot3_world simulation
    turtlebot3_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_gazebo_dir, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    # Map server - loads the pre-built map
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[amcl_params, {'yaml_filename': map_yaml_path}],
    )

    # AMCL - particle filter localization
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params],
    )

    # Lifecycle manager - brings map_server and amcl through configure/activate
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }],
    )

    return LaunchDescription([
        turtlebot3_world,
        map_server_node,
        amcl_node,
        lifecycle_manager_node,
    ])