#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient


# Наш action
from my_action_interface.action import SummCalculate
from my_custom_interface.msg import Numbers

class SummCalculateActionClient(Node):
    def __init__(self):
        super().__init__('summ_calculate_action_client')
        self._action_client = ActionClient(self, SummCalculate, 'summ_calculate')
        self._goal_handle = None
        self._pending_goal_handle = None
        self._subscription = self.create_subscription(
            Numbers,
            'numbers_topic',
            self.numbers_callback,
            10
        )
        self.get_logger().info('SummCalculateActionClient запущен!')

    def numbers_callback(self, msg):
        """
        Обработчик сообщений из топика numbers_topic.
        """
        a = msg.a
        b = msg.b
        if a == 0 and b == 0:
            self.get_logger().info("Cancel goal request receved")
            self.cancel_goal()
        else:
            self.send_goal(a, b)


    def send_goal(self, a, b):
        """
        Отправка goal: считаем сумму от self._a до self._b.
        """
        goal_msg = SummCalculate.Goal()
        goal_msg.a = a
        goal_msg.b = b

        # Ждём доступности сервера
        self._action_client.wait_for_server()
        self.get_logger().info(f"Отправляем goal (a={a}, b={b})...")

        # Асинхронная отправка
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def cancel_goal(self):
        """
        Запрос на отмену текущей задачи.
        """
        if self._goal_handle is None:
            self.get_logger().info("Нет активной задачи для отмены!")
            return

        self.get_logger().info("Отправляем запрос на отмену...")
        cancel_future = self._goal_handle.cancel_goal_async()
        cancel_future.add_done_callback(self.cancel_done)

    def cancel_done(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info("Задача отменена успешно.")
        else:
            self.get_logger().info("Не удалось отменить задачу.")
        self._goal_handle = None

    def goal_response_callback(self, future):
        """
        Вызывается, когда сервер принял (или отклонил) goal.
        """
        self._pending_goal_handle = future.result()
        if not self._pending_goal_handle.accepted:
            self.get_logger().info("Задача отклонена сервером!")
            self._pending_goal_handle = None
            return

        self.get_logger().info("Задача ПРИНЯТА сервером!")
        self._goal_handle = self._pending_goal_handle
        self._pending_goal_handle = None

        # Ждём итог (Result)
        self._get_result_future = self._goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """
        Вызывается при получении feedback от сервера.
        """
        left_to_result = feedback_msg.feedback.left_to_result
        self.get_logger().info(f"[FEEDBACK] Осталось ещё {left_to_result} шагов")

    def get_result_callback(self, future):
        """
        Вызывается, когда сервер завершил задачу (succeed, abort, cancel).
        """
        result = future.result().result
        if result.success:
            self.get_logger().info("Задача завершена УСПЕШНО!")
        else:
            self.get_logger().warn("Задача завершена НЕУДАЧНО (abort/cancel).")
        # Освободим goal_handle, чтобы можно было отправить новый
        self._goal_handle = None


def main(args=None):
    rclpy.init(args=args)
    node = SummCalculateActionClient()
    try:
        rclpy.spin(node)  # Обработка всех колбэков
    except KeyboardInterrupt:
        node.get_logger().info("Остановка сервера по Ctrl+C")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
