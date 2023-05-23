# 로봇을 목표 대상까지 이동
# 회전후 자동 직진
import math
import time
import rclpy

from custom_interfaces.action import Maze  # 이동 동향 # 커스텀 액션임.
from geometry_msgs.msg import Twist  # 로봇의 선속도, 각속도를 위한 Message type
from nav_msgs.msg import Odometry  # 자유공간에서의 로봇의 절대적인 위치 / 회전 기능에 사용

from py_action_pkg.py_action_pkg.image_sub import ImageSubscriber  # 초록 박스 인식에 사용
from py_action_pkg.py_action_pkg.robot_controller import euler_from_quaternion  # quaternion에서 euler angle로 변환하는 함수.
# 우리가 아는 요 피치 로우로 바꾸는거임 / 회전 기능에 사용

from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from sensor_msgs.msg import LaserScan  # 충돌 전까지 로봇 직진 기능에 사용

direction_dict = {0: (-1 * math.pi / 2), 1: math.pi, 2: math.pi / 2, 3: 0.0}
direction_str_dict = {0: 'Up', 1: 'Right', 2: 'Down', 3: 'Left'}  # 이동 방향


class ApolloActionServer(Node):

    def __init__(self):
        super().__init__('action_server') #우리가 사용할 변수명으로 바꾸면 됨

        self.yaw = 0.0
        self.forward_distance = 0.0

        self.twist_msg = Twist() # 로봇의 선속도, 각속도를 나타내는 메시지 타입. linear, angular로 구성
        self.loop_rate = self.create_rate(5, self.get_clock())
        # 특정 토픽의 메시지를 구독하기 위한 부분 create_subscription
        # 직진 부분 1
        self.laser_sub = self.create_subscription(
            LaserScan, 'scan', self.laser_sub_cb, 10
        )
        #  회전 기능에 사용
        self.odom_sub = self.create_subscription(
            Odometry, 'odom', self.odom_sub_cb, 10
        )

        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.publish_callback)

        self._action_server = ApolloActionServer(  # action 서버 생성
            self, Maze, 'maze_action', self.execute_callback # 자기자신, 사용하는액션타입, 액션이름, 콜백
        )
        self.get_logger().info('=== Maze Action Server Started ====')

    # 충돌 전까지 로봇 직진 기능에 사용
    def laser_sub_cb(self, data):
        self.forward_distance = data.ranges[360] # 전방 거리인 360만 사용


    def odom_sub_cb(self, data):
        orientation = data.pose.pose.orientation
        _, _, self.yaw = euler_from_quaternion(orientation)
        # self.get_logger().info(f'yaw : {self.yaw}')

    def publish_callback(self):
        self.cmd_vel_pub.publish(self.twist_msg)

    #  회전 기능에 사용
    def turn_robot(self, euler_angle):
        self.get_logger().info(f'Robot Turns to {euler_angle}')

        turn_offset = 100  # 각도 한계

        while abs(turn_offset) > 0.087:  # 각도 한계가 너무 작으면 오류 뜸
            turn_offset = 0.7 * (euler_angle - self.yaw)  # 각속도의 갑작스러운 변화를 막아주는 역할
            self.twist_msg.linear.x = 0.0
            self.twist_msg.angular.z = turn_offset
            self.cmd_vel_pub.publish(self.twist_msg)

        self.stop_robot()  # 회전 이후 로봇 정지

    # 충돌 전까지 로봇 직진 기능에 사용
    def parking_robot(self):

        while self.forward_distance > 1.0:
            self.twist_msg.linear.x = 0.5
            self.twist_msg.angular.z = 0.0

            self.cmd_vel_pub.publish(self.twist_msg)

        self.stop_robot()

    def stop_robot(self):
        self.twist_msg.linear.x = 0.0
        self.twist_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.twist_msg)

        time.sleep(1)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback = Maze.Feedback()
        feedback.feedback_msg = ''

        for _, val in enumerate(goal_handle.request.turning_sequence):
            self.get_logger().info(f'Current Cmd: {val}')

            feedback.feedback_msg = f'Turning {direction_str_dict[val]}'

            self.turn_robot(direction_dict[val]) #회전
            self.parking_robot() #직진

            goal_handle.publish_feedback(feedback) #피드백 보내기
        # 이떄까지 동작에서 imageSubscriber는 불필요
        # 모든 execution을 마친 시점에서, ImageSubscriber를 1회 실행. -> 1회 캡쳐
        # 이를 통해 전방 이미지의 중간 pixel값을 얻을 수 있음.
        image_sub_node = ImageSubscriber()
        rclpy.spin_once(image_sub_node)
        center_pixel = image_sub_node.center_pixel

        # 전방 pixel값을 사용하여 초록 박스 앞인지의 유무를 판단.
        # 이는 곧 미로의 탈출지점에 도착했는지의 여부와 동일.
        if sum(center_pixel) < 300 and center_pixel[1] > 100:
            goal_handle.succeed()
            self.get_logger().warn('==== Succeed ====')
            result = Maze.Result()
            result.success = True
        else:
            goal_handle.abort()
            self.get_logger().error('==== Fail ====')
            result = Maze.Result()
            result.success = False

        return result


def main(args=None):
    rclpy.init(args=args)

    try:
        action_server = ApolloActionServer()#클래스 리턴값을 저장
        executor = MultiThreadedExecutor()  # MultiThreadedExecutor -> 여러 노드, 토픽, 서비스, 액션 등을 병렬로
        executor.add_node(action_server) #142 코드에서 초기화한 변수를 ROS2 Executor노드로 추가하는거임.
        try:
            executor.spin()
        except KeyboardInterrupt:
            action_server.get_logger().info('Keyboard Interrupt (SIGINT)')
        finally:
            executor.shutdown()
            action_server._action_server.destroy()
            action_server.destroy_node()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()