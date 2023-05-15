#include <chrono>
#include <cinttypes>
#include <memory>

// Deduction
#include <typeinfo>

#include "custom_interfaces/action/fibonacci.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

using Fibonacci = custom_interfaces::action::Fibonacci;
using GoalHandleFibonacci = rclcpp_action::ClientGoalHandle<Fibonacci>;

class FBActionClient : public rclcpp::Node {
private:
  rclcpp_action::Client<Fibonacci>::SharedPtr m_action_client;
  GoalHandleFibonacci::SharedPtr goal_handle;
  rclcpp::TimerBase::SharedPtr m_timer;

public:
  FBActionClient() : Node("fb_action_client"), goal_handle(nullptr) {
    m_action_client =
        rclcpp_action::create_client<Fibonacci>(this, "fibonacci");
		//0.5초 후 자동으로 send_goal을 request
    m_timer = create_wall_timer(std::chrono::milliseconds(500),
                                std::bind(&FBActionClient::send_goal, this));

    RCLCPP_INFO(get_logger(), "FB Action Client Node Created");
  }

  bool is_goal_handle_none() {
    bool is_goal_handle = goal_handle == nullptr ? true : false;
    return is_goal_handle;
  }

  const std::shared_future<GoalHandleFibonacci::WrappedResult>
  get_result_future() {
    auto result_future = m_action_client->async_get_result(goal_handle);
    return result_future;
  }

  const std::shared_future<
      std::shared_ptr<action_msgs::srv::CancelGoal_Response>>
  get_cancel_result_future() {
    auto cancel_result_future = m_action_client->async_cancel_goal(goal_handle);
    return cancel_result_future;
  }

  void send_goal() {
    using namespace std::placeholders;

    // timer cancel required for send goal once
    m_timer->cancel();

		// request하는 server가 존재하는지 10초간 대기하며, 아니면 자동 종료
    if (!m_action_client->wait_for_action_server(std::chrono::seconds(10))) {
      RCLCPP_ERROR(get_logger(), "Action server not available after waiting");
      rclcpp::shutdown();
    }

		//Goal message 준비
    auto goal_msg = Fibonacci::Goal();
    goal_msg.order = 10;

    auto send_goal_options =
        rclcpp_action::Client<Fibonacci>::SendGoalOptions();

    // TODO(Swimming): Cancel Logic
		// goal response callback, feedback callback, resutl callback을 모두 연동
		// async_send_goal을 통해 goal send를 수행.
    send_goal_options.goal_response_callback =
        std::bind(&FBActionClient::goal_response_callback, this, _1);
    send_goal_options.feedback_callback =
        std::bind(&FBActionClient::feedback_callback, this, _1, _2);
    send_goal_options.result_callback =
        std::bind(&FBActionClient::result_callback, this, _1);

    m_action_client->async_send_goal(goal_msg, send_goal_options);
  }

  void goal_response_callback(
      std::shared_future<GoalHandleFibonacci::SharedPtr> future) {
		//goal response의 결과에 따라 로그 출력
    goal_handle = future.get();

    if (!goal_handle)
      RCLCPP_ERROR(get_logger(), "Goal was rejected by server");
    else
      RCLCPP_INFO(get_logger(), "Goal accepted by server, waiting for result");
  }

	//첫 매개변수인 goal_hanlde은 사용 안하고, feedback 메시지가 올 때마다 출력
  void
  feedback_callback(GoalHandleFibonacci::SharedPtr,
                    const std::shared_ptr<const Fibonacci::Feedback> feedback) {
    RCLCPP_WARN(get_logger(), "Next number in sequence received: ");

    for (auto number : feedback->partial_sequence)
      RCLCPP_INFO(get_logger(), "%d", number);
  }

	//switch를 통한 각 상황에 따른 처리를 진행
	//result인 sequence은 std:vector이므로 for-range로 순회 가능
  void result_callback(const GoalHandleFibonacci::WrappedResult &result) {
    switch (result.code) {
    case rclcpp_action::ResultCode::SUCCEEDED:
      break;
    case rclcpp_action::ResultCode::ABORTED:
      RCLCPP_ERROR(get_logger(), "Goal aborted");
      rclcpp::shutdown();
      return;
    case rclcpp_action::ResultCode::CANCELED:
      rclcpp::shutdown();
      RCLCPP_WARN(get_logger(), "Goal canceled");
      return;
    default:
      RCLCPP_ERROR(get_logger(), "Unknown result code");
      return;
    }

    RCLCPP_WARN(get_logger(), "Result received: ");

    for (const auto number : result.result->sequence)
      RCLCPP_INFO(get_logger(), "%d", number);

    rclcpp::shutdown();
  }
};
/*
main
1. Node 생성
2. timer에 의해 0.5초 후 send_goal 실행
3. Goal Response 도착 시 goal_handle 수령
4. get_result_future을 통해 Result Response future 수령
5. 받은 future을 통해 spin_until_future_complete를 실행시키고, 3초 안에 Result를 받지 못하면 Cancel이 시작
6. get_cancel_result_future를 통해 Cancel future를 받고, future의 결과에 따라 cancel 성공 여부를 판단.
*/
int main(int argc, char **argv) {
  rclcpp::init(argc, argv);

  auto client_node = std::make_shared<FBActionClient>();

  while (rclcpp::ok()) {
    rclcpp::spin_some(client_node);

    if (!client_node->is_goal_handle_none()) {
      auto result_future = client_node->get_result_future();
      auto wait_result = rclcpp::spin_until_future_complete(
          client_node, result_future, std::chrono::seconds(3));

      if (wait_result == rclcpp::executor::FutureReturnCode::TIMEOUT) {
        RCLCPP_INFO(client_node->get_logger(), "Canceling goal");
        // Cancel the goal since it is taking too long

        auto cancel_result_future = client_node->get_cancel_result_future();
        if (rclcpp::spin_until_future_complete(client_node,
                                               cancel_result_future) !=
            rclcpp::executor::FutureReturnCode::SUCCESS) {
          RCLCPP_ERROR(client_node->get_logger(), "failed to cancel goal");
          rclcpp::shutdown();
          return 1;
        }

        RCLCPP_INFO(client_node->get_logger(), "goal is being canceled");

        while (rclcpp::ok())
          rclcpp::spin_some(client_node);
      } else if (wait_result != rclcpp::executor::FutureReturnCode::SUCCESS) {
        RCLCPP_ERROR(client_node->get_logger(), "failed to get result");
        rclcpp::shutdown();
        return 1;
      }
    }
  }

  rclcpp::shutdown();
  return 0;
}