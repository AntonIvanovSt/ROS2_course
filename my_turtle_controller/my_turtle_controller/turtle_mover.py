#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleMover(Node):
    def __init__(self):
        super().__init__("turtle_mover")
        self.publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        timer_period = 0.5

        linear_speed = self.declare_parameter("linear_speed", 2.0).value
        angular_speed = self.declare_parameter("angular_speed", 1.0).value

        self.timer = self.create_timer(timer_period, self.move_turtle)

        self.twist_msg = Twist()
        self.twist_msg.linear.x = linear_speed
        self.twist_msg.angular.z = angular_speed

    def move_turtle(self):
        self.publisher_.publish(self.twist_msg)
        self.get_logger().info(
            "Publishing turtle velocity: linear=%f, angular=%f"
            % (self.twist_msg.linear.x, self.twist_msg.angular.z)
        )


def main(args=None):
    rclpy.init(args=args)
    node = TurtleMover()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
