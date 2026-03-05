#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from turtlesim.srv import Spawn


class SpawnSecondTurtle(Node):
    """
    Запускает сервисный клиент /spawn,
    чтобы создать вторую черепашку turtle2 в координатах (1,1).
    """

    def __init__(self):
        super().__init__("spawn_second_turtle")
        self.client = self.create_client(Spawn, "spawn")

        # Дождёмся, пока сервис /spawn станет доступен
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Ожидание сервиса /spawn ...")

        self.spawn_turtle()

    def spawn_turtle(self):
        request = Spawn.Request()
        request.x = 1.0
        request.y = 1.0
        request.theta = 0.0
        request.name = "turtle2"

        future = self.client.call_async(request)
        future.add_done_callback(self.callback_spawn)

    def callback_spawn(self, future):
        try:
            response = future.result()
            self.get_logger().info(
                f"Вторая черепашка успешно заспавнена: {response.name}"
            )
        except Exception as e:
            self.get_logger().error(f"Ошибка при спавне черепашки: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    node = SpawnSecondTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
