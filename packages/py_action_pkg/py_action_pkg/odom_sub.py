
import cv2

from nav_msgs.msg import Odometry
import numpy as np
import rclpy
from rclpy.node import Node



def euler_from_quaternion(quaternion):  # quaternion -> euler angle

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


class OdometrySubscriber(Node):


    def __init__(self):

        super().__init__('odom_subscriber')
        self.sub_period = 10  # Hz

        self.subscription = self.create_subscription( # 로봇으로부터 odom subscribe
            Odometry,
            'diffbot/odom',
            self.listener_callback,
            self.sub_period,
        )
        self.subscription

    def listener_callback(self, data):
        orientation = data.pose.pose.orientation# 변환하는 과정이 odom->pose ->pose -> orientation에서 변환이라 이렇게 써야함
        _, _, self._yaw = euler_from_quaternion(orientation) #Yaw만 사용하니까 quaternion을 사용해서 yaw만 변환

        self.get_logger().info(f"Current Yaw Angle : {self._yaw}")#출력문 각도는 라디안
def main(args=None):

    rclpy.init(args=args)

    Odometry_subscriber = OdometrySubscriber()

    rclpy.spin(Odometry_subscriber)

    Odometry_subscriber.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()