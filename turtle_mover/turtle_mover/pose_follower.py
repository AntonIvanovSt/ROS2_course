#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class TurtlePoseFollower(Node):
    def __init__(self):
        super().__init__("turtle_pose_follower")
        self.pose_subscriber = self.create_subscription(
            Pose, "/turtle1/pose", self.pose_callback, 10
        )

        self.publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)

        self.current_pose = Pose()

        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.control_loop)

        self.x_goal = 0.0
        self.y_goal = 0.0

        self.linear_k = 1.0
        self.angular_k = 4.0

        self.arrival_tolerance = 0.01

        self.reached = False
        self.unreachable = False

        self.last_distance = float("inf")
        self.last_progress_time = self.get_clock().now().nanoseconds
        self.no_progress_limit = 2.0

    def set_goal(self, x, y):
        self.x_goal = x
        self.y_goal = y

        self.reached = False
        self.unreachable = False

        self.last_distance = float("inf")
        self.last_progress_time = self.get_clock().now().nanoseconds

    def stop_moving(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.publisher_.publish(twist)

    def pose_callback(self, msg: Pose):
        self.current_pose = msg

    def control_loop(self):
        if self.reached or self.unreachable:
            return

        dx = self.x_goal - self.current_pose.x
        dy = self.y_goal - self.current_pose.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.arrival_tolerance:
            self.stop_moving()
            self.reached = True
            self.get_logger().info("Goal reached. Stopping.")
            return

        current_time = self.get_clock().now().nanoseconds
        if distance < self.last_distance - 0.01:
            self.last_progress_time = current_time
            self.last_distance = distance
        else:
            time_no_progress = (current_time - self.last_progress_time) / 1e9
            if time_no_progress > self.no_progress_limit:
                self.stop_moving()
                self.unreachable = True
                self.get_logger().warn("Goal is unreachable. Stopping.")

        desired_angle = math.atan2(dy, dx)
        angle_error = desired_angle - self.current_pose.theta
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        twist = Twist()

        twist.linear.x = self.linear_k * distance
        if twist.linear.x > 2.0:
            twist.linear.x = 2.0

        twist.angular.z = self.angular_k * angle_error
        if twist.angular.z > 2.0:
            twist.angular.z = 2.0
        elif twist.angular.z < -2.0:
            twist.angular.z = -2.0

        self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TurtlePoseFollower()

    try:
        while rclpy.ok():
            user_input = input("\nInsert x y (q to exit): ").strip()
            if not user_input:
                continue
            if user_input.lower() == "q":
                print("Exiting.")
                break

            coords = user_input.split()
            if len(coords) < 2:
                print("Wrong input. Usage: x y or q to exit")
                continue

            try:
                x_goal = float(coords[0])
                y_goal = float(coords[1])
            except ValueError:
                print("Invalid coordinates.")
                continue

            node.set_goal(x_goal, y_goal)
            node.get_logger().info(f"Go to (x={x_goal:.2f}, y={y_goal:.2f})...")

            while rclpy.ok() and not node.reached and not node.unreachable:
                rclpy.spin_once(node, timeout_sec=0.1)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
