#!/usr/bin/env python3

import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleMover(Node):
    def __init__(self):
        super().__init__("turtle_mover")
        self.publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)

        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.move_turtle)
        self.last_progress_time = self.get_clock().now().nanoseconds

        self.straight_time = 2.0
        self.turning_time = 2.0

        self.linear_speed = 2.0
        self.angular_speed = math.pi / 4  # 0.785 rad/s

        self.turning = False

        self.twist_msg = Twist()
        self.twist_msg.linear.x = self.linear_speed
        self.twist_msg.angular.z = 0.0

    def move_turtle(self):
        current_time = self.get_clock().now().nanoseconds
        moving_time = (current_time - self.last_progress_time) / 1e9

        if self.turning:
            if moving_time > self.turning_time:
                self.turning = False
                self.twist_msg.linear.x = self.linear_speed
                self.twist_msg.angular.z = 0.0
                self.last_progress_time = current_time
        else:
            if moving_time > self.straight_time:
                self.turning = True
                self.twist_msg.angular.z = self.angular_speed
                self.twist_msg.linear.x = 0.0
                self.last_progress_time = current_time

        self.publisher_.publish(self.twist_msg)
        self.get_logger().info(
            "Sending velocity: linear=%f, angular=%f"
            % (self.twist_msg.linear.x, self.twist_msg.angular.z)
        )


def main(args=None):
    rclpy.init(args=args)
    node = TurtleMover()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
