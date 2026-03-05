#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import numpy as np

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import Twist


class TurtleTf2Listener(Node):
    """
    Узел, который с помощью TF2 узнаёт позицию turtle1 относительно turtle2
    и двигает turtle2 к turtle1, публикуя скорость в /turtle2/cmd_vel.
    """

    def __init__(self):
        super().__init__("turtle_tf2_listener")

        # TF2: Buffer и TransformListener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Публикуем скорости для turtle2
        self.publisher = self.create_publisher(Twist, "/turtle2/cmd_vel", 10)

        # Таймер на каждую 0.5 секунды
        self.timer = self.create_timer(0.5, self.on_timer)

    def on_timer(self):
        try:
            # Спрашиваем: "Как выглядит turtle1 в координатах turtle2?"
            transform = self.tf_buffer.lookup_transform(
                "turtle2",  # Целевой фрейм
                "turtle1",  # Исходный фрейм
                rclpy.time.Time(),
            )
        except TransformException as ex:
            self.get_logger().warn(f"Нет трансформации: {ex}")
            return

        dx = transform.transform.translation.x
        dy = transform.transform.translation.y

        distance = np.hypot(dx, dy)
        angle = np.arctan2(dy, dx)

        cmd = Twist()
        cmd.linear.x = 1.0 * distance
        cmd.angular.z = 3.0 * angle

        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleTf2Listener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
