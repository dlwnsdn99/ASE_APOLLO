// Client로 request를 받으면 time_duration 동안 angular_vel_z, linear_vel_x를 갖고 로봇 이동
// $ ros2 run cpp_service_pkg robot_turning_server 로 실행
// 아래는 robot_turning_server.cpp 의 코드임

#include <memory>
#include "custom_interfaces/srv/turning_control.hpp" //사용자 지정 srv 타입 사용을 위한 헤더파일
#include "geometry_msgs/msg/twist.hpp" //사용자 지정 srv 타입 사용을 위한 헤더파일
#include "rclcpp/rclcpp.hpp" //사용자 지정 srv 타입 사용을 위한 헤더파일

using Twist = geometry_msgs::msg::Twist; //using으로 타입 길이 줄이기
using TurningControl = custom_interfaces::srv::TurningControl; //using으로 타입 길이 줄이기

class RobotTurnServer : public rclcpp::Node {
private:
  rclcpp::Service<TurningControl>::SharedPtr m_service;//제어신호를 받는 service server 생성 위함
  rclcpp::Publisher<Twist>::SharedPtr m_twist_pub;//로봇을 움직일 topic publisher 생성 위함

  Twist m_twist_msg;

public:
  RobotTurnServer() : Node("robot_turn_server") {
    RCLCPP_WARN(get_logger(), "Robot Turn Server Started");

    m_twist_pub = create_publisher<Twist>("skidbot/cmd_vel", 10); //로봇을 움직일 topic publisher 생성

    m_service = create_service<TurningControl>(
        "turn_robot", std::bind(&RobotTurnServer::response_callback, this,
                                std::placeholders::_1, std::placeholders::_2));
		//사용하는 srv 타입 : TurningControl
		//생성할 service명 : turn_robot
		//request시 생성될 response callback : std::bind(&RobotTurnServer::response_callback, this,std::placeholders::_1, std::placeholders::_2));
	  
		//Server는 요구 파악(request) -> 요구에 따른 연산 수행 -> response에 연산 결과를 포함해서 보냄 
		//그래서 callback의 매개변수에 request, response가 매개변수로 필요함
	}

	// 미리 생성한 srv타입
  // uint32 time_duration
  // float64 angular_vel_z
  // float64 linear_vel_x
  // ---
  // bool success

	// Client에서 requesttl rclcpp가 아래 함수로 연결
	// 매개변수로 request, response 모두 필요
  void response_callback(std::shared_ptr<TurningControl::Request> request,
                         std::shared_ptr<TurningControl::Response> response) 
	{
		//시간
    auto t_start = now();
    auto t_now = now();
    auto t_delta = request->time_duration * 1e9;

    RCLCPP_INFO(get_logger(), "\nTime Duration : %d\nLinear X Cmd : %f\nAngular Z Cmd : %f",
      request->time_duration, request->linear_vel_x, request->angular_vel_z);

    RCLCPP_INFO(get_logger(), "Request Received Robot Starts to Move");

    while ((t_now - t_start).nanoseconds() < t_delta) {
      t_now = now();
      move_robot(request->linear_vel_x, request->angular_vel_z);
    }
		//publish에는 spin사용x
    stop_robot();

    RCLCPP_WARN(get_logger(), "Request Done Wating for next request...");
	  //여기에 상황에 따라 예외처리 추가 가능
		response->success = true;
  }
	
	//로봇 제어는 Topic
  void move_robot(const float &linear_x, const float &angular_z) {
    m_twist_msg.linear.x = linear_x;
    m_twist_msg.angular.z = angular_z;

    m_twist_pub->publish(m_twist_msg);
  }

  void stop_robot() {
    m_twist_msg.linear.x = 0.0;
    m_twist_msg.angular.z = 0.0;
    m_twist_pub->publish(m_twist_msg);

    RCLCPP_INFO(get_logger(), "Stop Robot and make Node FREE!");
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);

  auto node = std::make_shared<RobotTurnServer>();

  rclcpp::spin(node);
  rclcpp::shutdown();
}