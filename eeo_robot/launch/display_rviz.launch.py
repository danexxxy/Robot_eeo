import launch
import launch_ros
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('eeo_robot')
    urdf_path = os.path.join(pkg_share, 'urdf', 'eeo_robot.urdf')

    with open(urdf_path, 'r') as f:
        robot_description_content = f.read()

    measure_node = launch_ros.actions.Node(
        package='eeo_robot',
        executable='measure',
        name='measure_node'
    )

    state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    joint_state_publisher_node = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2'
    )
    
    static_tf_node = launch_ros.actions.Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'base_link']
    )

    return launch.LaunchDescription([
        measure_node,
        state_publisher_node,
        joint_state_publisher_node,
        rviz_node,
        static_tf_node
    ])

