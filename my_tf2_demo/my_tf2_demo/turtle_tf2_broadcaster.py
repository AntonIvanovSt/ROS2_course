#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import numpy as np

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose


class TurtleTf2Broadcaster(Node):
    """
    Подписывается на /<turtle_name>/pose и публикует трансформацию
    world -> <turtle_name> в TF2.
    """

    def __init__(self):
        super().__init__("tf2_broadcaster_")

        self.declare_parameter("turtle_name", "turtle1")
        self.turtle_name = self.get_parameter("turtle_name").value

        # Подписка на топик позы конкретной черепашки
        self.sub = self.create_subscription(
            Pose, f"/{self.turtle_name}/pose", self.handle_turtle_pose, 10
        )

        # Инициализируем TF2 Broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

    def handle_turtle_pose(self, msg: Pose):
        # Создаём сообщение TransformStamped
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "world"  # Родительский фрейм
        t.child_frame_id = self.turtle_name  # Дочерний фрейм

        # Перенос (x, y) — берем из Pose
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0

        # Преобразуем угол поворота (yaw) в кватернион
        q = self.quaternion_from_euler(0, 0, msg.theta)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        # Публикуем трансформацию
        self.tf_broadcaster.sendTransform(t)

    @staticmethod
    def quaternion_from_euler(roll, pitch, yaw):
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)
        # Для 2D-сценария roll=pitch=0 => qx=qy=0
        return [0.0, 0.0, sy, cy]


def main(args=None):
    rclpy.init(args=args)
    node = TurtleTf2Broadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
