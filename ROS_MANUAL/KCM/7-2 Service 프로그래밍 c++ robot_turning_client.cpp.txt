//$ ros2 run cpp_service_pkg robot_turning_client 5 0.5 1.0 이렇게 실행
//srv 타입은 custom
//사용자 srv 생성법은 구글링 해야함
#include <chrono>
#include <cstdlib>
#include <memory>

#include "custom_interfaces/srv/turning_control.hpp" //사용자 srv사용 헤더파일
#include "rclcpp/rclcpp.hpp" //사용자 srv사용 헤더파일

using namespace std::chrono_literals;
using TurningControl = custom_interfaces::srv::TurningControl;

class RobotTurnClient : public rclcpp::Node
{
private:
	// Service Client 선언
  rclcpp::Client<TurningControl>::SharedPtr m_client;
  std::shared_ptr<TurningControl::Request> m_request;

public:
  RobotTurnClient() : Node("robot_turn_client")
  {
    m_client = create_client<TurningControl>("turn_robot");
		//사용하는 srv타입, request할 service이름
    m_request = std::make_shared<TurningControl::Request>();
		// request할 server가 없으면 기다리며 log 출력
    while (!m_client->wait_for_service(1s))
      RCLCPP_INFO(get_logger(), "service not available, waiting again...");
		// server 찾으면 다음 log 출력
    RCLCPP_INFO(get_logger(), "service available, waiting serice call");
  }

	// srv type
  // uint32 time_duration
  // float64 angular_vel_z
  // float64 linear_vel_x
  // ---
  // bool success

	//request를 보내고 future를 반환
  auto get_result_future(const int &time_in, const float &linear_x_in,
                         const float &angular_z_in)
  {
    RCLCPP_WARN(get_logger(), "Input Info");
    RCLCPP_INFO(get_logger(), "time_duration : %d\nlinear_vel_x : %f\nangular_vel_z : %f",
      time_in, linear_x_in, angular_z_in);

    m_request->time_duration = time_in;
    m_request->linear_vel_x = linear_x_in;
    m_request->angular_vel_z = angular_z_in;

		// async:비동기
		// server부터 response가 오기 전까지 다른 일 하며 대기
    return m_client->async_send_request(m_request);
  }
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
	// node 실행 시 받은 매개변수에 대한 예외 처리
  if (argc != 4)
  {
    RCLCPP_INFO(
        rclcpp::get_logger("rclcpp"),
        "usage: robot_turning_client [seconds] [linear_vel_x] [angular_vel_z]");
    return 1;
  }

  auto basic_service_client = std::make_shared<RobotTurnClient>();

	//atoi : 문자열 -> 정수
	//atof : 문자열 -> 부동소수점 자료형
	//get_result_future를 통해 request 정보를 전달하고 result를 리턴으로 받음
  auto result = basic_service_client->get_result_future(
      atoi(argv[1]), atof(argv[2]), atof(argv[3]));


  // Wait for the result.
	// 결과에 따라 성공 실패 여부 표기
	// spin으로 result 기다림. spin_until_future_complete
	// ros2 강의에 따르면 future이란
		// 세탁기 돌리기, 햇반 돌리기, 청소하기를 동시에 하는 자취생한테 들리는 전자레인지 소리이다.
	// 즉 response가 즉시 이뤄지지 않을 때 service request동안 다른 일을 하다 response가 오는 시점에
	//돌아와 그 결과를 수령함 -> 이게 비동기 방식이고 영어론 asynchronous
  if (rclcpp::spin_until_future_complete(basic_service_client, result) ==
      rclcpp::executor::FutureReturnCode::SUCCESS)
		// 이 함수의 input : future과 future이 속한 node
		// 이 함수의 output : SUCCESS, INTERRUPTED, TIMEOUT
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Result : %s",
                result.get()->success ? "True" : "False");
  else
    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"),
                 "Failed to call service add_two_ints");

  rclcpp::shutdown();
  return 0;
}