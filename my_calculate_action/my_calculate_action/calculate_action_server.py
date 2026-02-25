#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from my_action_interface.action import SummCalculate


class SummCalculateActionServer(Node):
    """
    Action-сервер, который считает сумму целых чисел от a до b, a <= b.
    Каждое сложение выполняется в колбэке таймера, чтобы сервер оставался отзывчивым.
    """

    def __init__(self):
        super().__init__('summ_calculate_action_server')

        # Создаём Action-сервер
        self._action_server = ActionServer(
            self,
            SummCalculate,
            'summ_calculate',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            handle_accepted_callback=self.handle_accepted_callback,
        )

        self.get_logger().info("SummCalculate Action Server Запущен!")

        # Переменные для состояния задачи
        self._timer = None
        self._current_goal = None
        self._current_sum = 0
        self._current_step = 0
        self._end = 0
        self._task_active = 0
        self._is_cancelled = 0

    def _reset_task_state(self):
        """
        Сбрасывает все переменные, связанные с текущей задачей.
        """
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self._current_goal = None
        self._current_sum = 0
        self._current_step = 0
        self._end = 0
        self._task_active = 0
        self._is_cancelled = 0
        self.get_logger().info("Все переменные задачи сброшены.")

    def goal_callback(self, goal_request):
        """
        Вызывается при поступлении нового Goal.
        """
        if self._task_active == 1:
            self.get_logger().warn(f"Текущая задача еще выполняется. Отмените ее.")
            return GoalResponse.REJECT

        self._task_active = 1

        self.get_logger().info(f'Получен goal: a={goal_request.a}, b={goal_request.b}')
        if goal_request.a > goal_request.b:
            self.get_logger().error("Некорректный диапазон (a > b). Отклоняем задачу.")
            self._task_active = 0
            return GoalResponse.REJECT
        self._current_step = goal_request.a
        self._end = goal_request.b

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
        """
        Метод вызывается, когда цель (goal) принимается сервером. Он инициализирует выполнение 
        задачи и запускает таймер для асинхронного выполнения.
        
        Логика:
        1. Связывает текущую цель с внутренней переменной `_current_goal`.
        2. Устанавливает флаг `_task_active`, указывающий на активность задачи.
        3. Создаёт таймер с интервалом 0.1 секунды для выполнения шагов задачи в 
        `timer_callback`.
        """
        self.get_logger().info("Задача принята. Начинаем выполнение...")
        self._current_goal = goal_handle
        # Запускаем таймер
        self._timer = self.create_timer(0.1, self.timer_callback)


    def execute_callback(self, goal_handle):
        """
        Этот метод отвечает за выполнение задачи до её завершения или отмены. 
        Он формирует результат задачи и завершает её состояние.
        
        Логика:
        1. Если задача была отменена, метод устанавливает состояние "прервана" через 
        `goal_handle.abort()`.
        2. Если задача успешно завершена, устанавливает состояние "выполнено" через 
        `goal_handle.succeed()`.
        3. После завершения задачи вызывается метод `_reset_task_state()` 
        для очистки состояния сервера.
        """
        result = SummCalculate.Result()

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
        Колбэк таймера отвечает за выполнение одного шага вычислений.
        
        Логика:
        1. Проверяет, была ли задача отменена. Если да, завершает таймер и очищает состояние.
        2. Если текущий шаг превышает конечное значение (_end), завершает задачу.
        3. Выполняет сложение текущего числа (_current_step) к сумме (_current_sum).
        4. Публикует обратную связь (feedback) о количестве оставшихся шагов.
        """
        if self._current_goal is None or self._current_goal.is_cancel_requested:
            # Если задача отменена, завершить таймер
            self.get_logger().info("Задача отменена. Останавливаем выполнение.")
            self._is_cancelled = 1
            self._task_active = 0
            self._current_goal.abort()
            return
        if self._current_goal.status == 1 and self._task_active == 0:
            self._task_active = 1
            self.get_logger().info("Начато выполнение задачи.")
            # Инициализируем параметры задачи
            self._current_sum = 0
            self._current_step = self._current_goal.request.a
            self._end = self._current_goal.request.b

        if self._current_step > self._end:
            # Завершение задачи
            self.get_logger().info(f"Вычисление завершено. Сумма: {self._current_sum}")
            self._task_active = 0
            self._is_cancelled = 0
            self._current_goal.execute()
            return

        # Выполняем шаг
        self._current_sum += self._current_step
        self._current_step += 1

        # Публикуем обратную связь
        feedback = SummCalculate.Feedback()
        feedback.left_to_result = self._end - self._current_step + 1
        self._current_goal.publish_feedback(feedback)
        self.get_logger().info(f"Текущая сумма: {self._current_sum}, "
            "осталось шагов: {feedback.left_to_result}")


def main(args=None):
    rclpy.init(args=args)
    server = SummCalculateActionServer()
    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        server.get_logger().info("Остановка сервера по Ctrl+C")
    finally:
        server.destroy_node()
        rclpy.shutdown()
        server.get_logger().info("Сервер остановлен.")


if __name__ == '__main__':
    main()
