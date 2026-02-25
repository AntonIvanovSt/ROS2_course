#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from my_custom_interface.msg import Numbers
import signal


class NumberPublisherNode(Node):
    def __init__(self):
        super().__init__('number_publisher')
        self.publisher_ = self.create_publisher(Numbers, 'numbers_topic', 10)
        self.shutdown_called = False  # Флаг предотвращает повторное выключение
        self.get_logger().info('Number Publisher Node запущена!')

        # Устанавливаем обработчик Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

    def publish_numbers(self):
        """
        Функция для чтения чисел из input() и публикации их в топик.
        Завершается при 'q' или Ctrl+C.
        """
        try:
            while rclpy.ok():
                try:
                    user_input = input("Введите два числа (например, '5 10') "
                        "или 'q' для выхода or 0 0 for cancel: ").strip()
                    
                    if user_input.lower() == 'q':
                        self.get_logger().info('Завершение работы по вводу "q".')
                        break

                    # Парсим ввод пользователя
                    a, b = map(int, user_input.split())
                    msg = Numbers()
                    msg.a = a
                    msg.b = b

                    # Публикуем сообщение
                    self.publisher_.publish(msg)
                    if a == 0 and b == 0:
                        self.get_logger().info("Publish cancel goal")
                    else:
                        self.get_logger().info(f'Опубликованы числа: a={a}, b={b}')
                except ValueError:
                    self.get_logger().info("Invalid data. Try again.")


        except (ValueError, EOFError):
            self.get_logger().warn("Некорректный ввод! Попробуйте снова.")
        finally:
            self.shutdown()

    def shutdown(self):
        """Pавершение ноды"""
        if not self.shutdown_called:  # Проверяем, не был ли уже вызван shutdown
            self.shutdown_called = True

            if rclpy.ok():
                self.get_logger().info("Остановка ноды.")
            
            self.destroy_node()

            if rclpy.ok():
                rclpy.shutdown()

    def signal_handler(self, signum, frame):
        """Обработчик Ctrl+C"""
        if not self.shutdown_called:
            self.get_logger().info("Завершение работы по Ctrl+C.")
        self.shutdown()
        exit(0)


def main(args=None):
    rclpy.init(args=args)
    node = NumberPublisherNode()

    try:
        node.publish_numbers()
    finally:
        node.shutdown()


if __name__ == '__main__':
    main()

