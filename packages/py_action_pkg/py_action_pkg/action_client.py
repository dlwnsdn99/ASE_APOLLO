#!/usr/bin/env/ python3

from custom_interfaces.action import Maze
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

class ApolloActionClient(Node):

    def __init__(self):
        super().__init__('action_client')
        self.action_client = ApolloActionClient(self, Maze, 'diffbot/maze_action')
        self.get_logger().info('=== Maze Action Client Started ====')

    def send_goal(self, turning_list):
        goal_msg = Maze.Goal()
        goal_msg.turning_sequence = turning_list

        if self.action_client.wait_for_server(10) is False:
            self.get_logger().error('Server Not exists')

        self._send_goal_future = self.action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_message):
        feedback = feedback_message.feedback
        self.get_logger().info(f'Received feedback: {feedback.feedback_msg}')

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().warn(f'Action Done !! Result: {result.success}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    action_client = ApolloActionClient()
    user_inputs = []

    # Input Logic
    try:
        action_client.get_logger().info('Enter numbers [or stop] : ')

        while True:
            user_inputs.append(int(input()))
    # if the input is not-integer, just print the list
    except Exception:
        action_client.get_logger().info(f'Your sequence list : {user_inputs}')
    action_client.get_logger().info('==== Sending Goal ====')
    action_client.send_goal(user_inputs)


    rclpy.spin(action_client)


if __name__ == '__main__':
    main()