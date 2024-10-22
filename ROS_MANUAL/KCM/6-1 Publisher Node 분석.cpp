// 로봇을 움직이기 위해선 geometry_msgs/msg/Twist 형식의 topic message type 사용해야함.
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
//이 두개 헤더가 그걸 지원해줌.
////만약 ros2 interface show를 했을때 나온 message type이 CammelCase면 c++헤더는 snake_case

//클래스 내부의 핵심은 Publisher를 생성하고 publish하는 것.
//1. create_publisher
//create_publisher 함수를 통해 생성함
m_pub = create_publisher<geometry_msgs::msg::Twist>("skidbot/cmd_vel", 10);
//<message type>("생성할 topic 이름", queue size)

//message의 publish는 node가 가진 publish함수에 message를 전달함.
//예시의 m_pub는 포인터라서 ->로 접근
m_pub->publish(m_twist_msg);

//////////////////////////////////////////////////////////////////
//2.ROS2 C++ 시간 API
//node->now() 하면 현재 시간. rclcpp::Time 타입
  auto t_start = twist_pub->now();
  auto t_now = twist_pub->now();

	auto stop_time = 5.0; //5초

	// 정해진 시간 동안만 publish하기 위해 spin_some을 사용
	//예시 상으로 5초 반복후 while문 탈출, 로봇 정지
  while ((t_now - t_start).seconds() < stop_time)
  {
    t_now = twist_pub->now();
		// rclcpp::spin_some(twist_pub);
    twist_pub->move_robot();

		// 경과 시간을 콘솔로 출력
		RCLCPP_INFO(twist_pub->get_logger(), "%f Seconds Passed", (t_now - t_start).seconds());
  }
