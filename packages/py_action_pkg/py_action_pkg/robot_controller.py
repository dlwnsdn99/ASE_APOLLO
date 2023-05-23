# !/usr/bin/env/ python3

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

def euler_from_quaternion(quaternion):

    x = quaternion.x
    y = quaternion.y
    z = quaternion.z
    w = quaternion.w

    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    pitch = np.arcsin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


class RobotController(Node):

    def __init__(self):

        super().__init__('robot_controller')

        self.rate = self.create_rate(5)

        self.ok = False
        self.yaw = 0.0
        self.forward_distance = 0.0
        self.twist_msg = Twist()

        self.sub_period = 10  # Hz
        self.pub_period = 10  # Hz

        self.laser_sub = self.create_subscription(
            LaserScan, 'diffbot/scan', self.laser_sub_cb, self.sub_period
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            'diffbot/odom',
            self.odom_sub_cb,
            self.sub_period,
        )

        self.cmd_vel_pub = self.create_publisher(
            Twist, 'diffbot/cmd_vel', self.pub_period
        )

        self.cmd_vel_pub
        self.laser_sub
        self.odom_sub
        self.get_logger().info('====Robot Control Node Started ====\n')

    def is_ok(self):
        return self.ok

    def odom_sub_cb(self, data):
        orientation = data.pose.pose.orientation
        _, _, self.yaw = euler_from_quaternion(orientation)

    def laser_sub_cb(self, data):
        self.forward_distance = data.ranges[360]

    def move_robot(self, linear_vel=0.0):
        self.twist_msg.linear.x = linear_vel
        self.twist_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.twist_msg)

    def stop_robot(self):
        self.get_logger().info('====Stop Robot ====')
        self.twist_msg.linear.x = 0.0
        self.twist_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.twist_msg)

    def turn_robot(self, angular_vel=0.0):
        self.twist_msg.linear.x = 0.0
        self.twist_msg.angular.z = angular_vel
        self.cmd_vel_pub.publish(self.twist_msg)


def turn_robot(rclpy, controller, euler_angle):
    print('Robot Turns to Object Angle')

    controller.stop_robot()

    while rclpy.ok():
        rclpy.spin_once(controller)
        turn_offset = 0.7 * (euler_angle - controller.yaw)
        controller.turn_robot(turn_offset)

        if abs(turn_offset) < 0.005:
            rclpy.spin_once(controller)
            controller.stop_robot()
            rclpy.spin_once(controller)
            break

    controller.stop_robot()


def parking_robot(rclpy, controller):
    print('Going Forward Until 0.8m Obstacle Detection')

    controller.stop_robot()

    while rclpy.ok():
        rclpy.spin_once(controller)
        controller.move_robot(0.5)

        if controller.forward_distance < 0.8:
            rclpy.spin_once(controller)
            controller.stop_robot()
            rclpy.spin_once(controller)
            break


def main(args=None):
    rclpy.init(args=args)

    robot_controller = RobotController()

    while True:
        robot_controller.move_robot(1.0)
        robot_controller.get_logger().info(robot_controller.forward_distance)

    robot_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()