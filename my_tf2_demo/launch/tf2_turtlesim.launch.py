#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # 1) Запускаем симуляцию turtlesim
    turtlesim_node = Node(package="turtlesim", executable="turtlesim_node", name="sim")

    # 2) Узел, который спавнит вторую черепашку
    spawn_node = Node(
        package="my_tf2_demo",
        executable="spawn_second_turtle",
        name="spawn_second_turtle",
    )

    # 3) TF2 Broadcaster для turtle1
    broadcaster1 = Node(
        package="my_tf2_demo",
        executable="turtle_tf2_broadcaster",
        name="tf2_broadcaster_turtle1",
        parameters=[{"turtle_name": "turtle1"}],  # Передаём параметр
    )

    # 4) TF2 Broadcaster для turtle2
    broadcaster2 = Node(
        package="my_tf2_demo",
        executable="turtle_tf2_broadcaster",
        name="tf2_broadcaster_turtle2",
        parameters=[{"turtle_name": "turtle2"}],
    )

    # 5) Запуск Listener
    listener_node = Node(
        package="my_tf2_demo", executable="turtle_tf2_listener", name="tf2_listener"
    )

    return LaunchDescription(
        [turtlesim_node, spawn_node, broadcaster1, broadcaster2, listener_node]
    )
