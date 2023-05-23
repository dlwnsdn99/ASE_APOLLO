# Gazebo를 실행시킨 상태에서
#ros2 topic list
#$ ros2 run image_view image_view --ros-args --remap /image:=/diffbot/camera_sensor/image_raw

import cv2

from cv_bridge import (
    CvBridge,
    CvBridgeError,
)

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image

class ImageSubscriber(Node):

    def __init__(self):

        super().__init__("image_subscriber")
        self.sub_period = 10  # Hz

        # topic subscriber를 생성
        self.subscription = self.create_subscription(
            Image,
            "/diffbot/camera_sensor/image_raw",
            self.listener_callback,
            self.sub_period,
        )
        self.subscription

        # ROS2 <=> OpenCV를 해주는 cv_bridge
        self.cv_bridge = CvBridge()

    def listener_callback(self, data): # ROS2 image -> OpenCV image

        try:
            current_frame = self.cv_bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            self.get_logger().info(e)

        #다음 코드를 주석 해제하면 카메라 시점으로 볼 수 있음
        #cv2.imshow("camera", current_frame)
        #cv2.waitKey(1)

        self.center_pixel = current_frame[400, 400]


def main(args=None):

    rclpy.init(args=args)

    image_subscriber = ImageSubscriber()

    rclpy.spin(image_subscriber)

    image_subscriber.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()