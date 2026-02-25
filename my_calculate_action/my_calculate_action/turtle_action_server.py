#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from my_action_interface.action import SummCalculate

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class TurtleActionServer(Node):
    """
    Action-сервер для управления черепашкой с обратной связью и проверкой достижимости цели.
    """

    def __init__(self):
        super().__init__('turtle_action_server')

        # Создаём Action-сервер
        self._action_server = ActionServer(
            self,
            SummCalculate,
            'turtle_move',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            handle_accepted_callback=self.handle_accepted_callback,
        )

        self.get_logger().info("Turtle Action Server Запущен!")

        # Подписчик для получения текущей позы черепашки
        self.pose_subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # Издатель для отправки команд движения
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Переменные для текущего состояния задачи
        self._timer = None
        self._current_goal = None
        self._current_pose = Pose()
        self._task_active = 0
        self._is_cancelled = 0
        self._x_goal = 0.0
        self._y_goal = 0.0

        # Переменные для проверки достижимости
        self.last_distance = float('inf')
        self.last_progress_time = None
        self.no_progress_limit = 2.0  # 2 секунды

        # Коэффициенты для P-регулятора
        self.linear_k = 1.0
        self.angular_k = 4.0
        self.arrival_tolerance = 0.1

    def stop_moving(self):
        """Останавливает черепашку, отправляя команды с нулевой скоростью."""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.publisher_.publish(twist)
        self.get_logger().info("Черепашка остановлена.")

    def _reset_task_state(self):
        """
        Сбрасывает все переменные, связанные с текущей задачей.
        """
        if self._timer:
            self._timer.cancel()
            self._timer = None
        #self._current_goal = None
        self._x_goal = 0.0
        self._y_goal = 0.0
        self._task_active = 0
        self._is_cancelled = 0
        self.last_distance = float('inf')
        self.last_progress_time = None
        self.stop_moving()
        self.get_logger().info("Все переменные задачи сброшены.")

    def pose_callback(self, msg: Pose):
        """Получение текущей позы черепашки."""
        self._current_pose = msg

    def goal_callback(self, goal_request):
        """
        Вызывается при поступлении нового Goal.
        """
        if self._task_active == 1:
            self.get_logger().warn("Текущая задача ещё выполняется. Отмените её.")
            return GoalResponse.REJECT

        self._task_active = 1
        self._is_cancelled = 0

        self._x_goal = goal_request.a
        self._y_goal = goal_request.b
        self.last_distance = float('inf')
        self.last_progress_time = self.get_clock().now().nanoseconds

        self.get_logger().info(f'Получен goal: x_goal={self._x_goal}, y_goal={self._y_goal}')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """
        Вызывается при запросе отмены задачи.
        """
        self.get_logger().warn("Получен запрос на отмену!")
        self._reset_task_state()
        self._is_cancelled = 1
        return CancelResponse.ACCEPT


    def handle_accepted_callback(self, goal_handle):
        self.get_logger().info("Задача принята. Начинаем выполнение...")
        self._current_goal = goal_handle
        # Запускаем таймер
        self._timer = self.create_timer(0.1, self.timer_callback)


    def execute_callback(self, goal_handle):
        """
        Выполняется при старте задачи. Завершается через succeed или abort.
        """

        result = SummCalculate.Result()

        # Блокировка, пока задача активна
        while self._task_active:
            rclpy.spin_once(self, timeout_sec=0.1)

        if self._is_cancelled:
            result.success = False
            goal_handle.abort()  # Устанавливаем состояние "прервана"
            self.get_logger().warn("Задача была прервана.")
        else:
            result.success = True
            goal_handle.succeed()  # Устанавливаем состояние "успешно выполнена"
            self.get_logger().info("Задача завершена успешно.")

        self._reset_task_state()  # Сбрасываем состояние
        return result

    def timer_callback(self):
        """
        Колбэк таймера: управляет движением черепашки и публикует обратную связь.
        """
        if self._current_goal is None or self._current_goal.is_cancel_requested:
            self.get_logger().info("Задача отменена. Останавливаем выполнение.")
            self._is_cancelled = 1
            self._task_active = 0
            self._current_goal.execute()
            return

        if self._current_goal.status == 1:
            self._task_active = 1
            self.get_logger().info("Начато выполнение задачи.")

        # Вычисляем расстояние до цели
        dx = self._x_goal - self._current_pose.x
        dy = self._y_goal - self._current_pose.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Проверяем, достигли ли мы цели
        if distance < self.arrival_tolerance:
            self.get_logger().info("Цель достигнута. Останавливаем черепашку.")
            self._task_active = 0
            self.stop_moving()
            self._current_goal.execute()
            return

        # Проверяем, есть ли прогресс
        current_time = self.get_clock().now().nanoseconds
        if distance < self.last_distance - 0.001:
            self.last_progress_time = current_time
            self.last_distance = distance
        else:
            time_no_progress = (current_time - self.last_progress_time) / 1e9
            if time_no_progress > self.no_progress_limit:
                self.get_logger().warn("Цель недостижима. Останавливаем черепашку.")
                self._is_cancelled = 1
                self._task_active = 0
                self.stop_moving()
                self._current_goal.execute()
                return

        # Управление по P-регулятору
        desired_angle = math.atan2(dy, dx)
        angle_error = desired_angle - self._current_pose.theta
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        twist = Twist()
        twist.linear.x = min(self.linear_k * distance, 2.0)
        twist.angular.z = max(min(self.angular_k * angle_error, 2.0), -2.0)
        self.publisher_.publish(twist)

        # Публикуем обратную связь
        if self._current_goal is not None:
            feedback = SummCalculate.Feedback()
            feedback.left_to_result = int(round(distance, 2))
            self._current_goal.publish_feedback(feedback)
            self.get_logger().info(f"[FEEDBACK] Расстояние до цели: {feedback.left_to_result}")


def main(args=None):
    rclpy.init(args=args)
    server = TurtleActionServer()
    try:
        server.get_logger().info("Сервер запущен, начинаем обработку целей.")
        rclpy.spin(server)
    except KeyboardInterrupt:
        server.get_logger().info("Остановка сервера по Ctrl+C")
    finally:
        server.destroy_node()
        rclpy.shutdown()
        server.get_logger().info("Сервер остановлен.")


if __name__ == '__main__':
    main()

