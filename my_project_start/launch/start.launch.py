#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Нода симуляции Turtlesim
    turtlesim_node = Node(package="turtlesim", executable="turtlesim_node", name="sim")

    # Нода управления черепашкой (из вашего пакета)
    turtle_mover_node = Node(
        package="my_turtle_controller",
        executable="turtle_mover",
        name="turtle_mover",
        parameters=[{"linear_speed": 1.0, "angular_speed": 0.5}],
    )

    return LaunchDescription([turtlesim_node, turtle_mover_node])
