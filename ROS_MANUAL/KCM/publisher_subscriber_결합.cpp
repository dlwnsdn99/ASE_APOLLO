#include <memory>
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

using Twist = geometry_msgs::msg::Twist;	//로봇 구동을 위한 twist형식
using LaserScan = sensor_msgs::msg::LaserScan;	//메시지 타입 쉽게 사용하기 위한 using 축약

class ParkingNode : public rclcpp::Node
{
private:
	// publisher, subscriber 요구
  	rclcpp::Publisher<Twist>::SharedPtr m_pub;
  	rclcpp::Subscription<LaserScan>::SharedPtr m_sub;

 	 Twist m_twist_msg;

public:
  	ParkingNode() : Node("robot_parking_node")
  	{
   	 RCLCPP_INFO(get_logger(), "Parking Node Created");
		
			// publisher와 subscriber를 모두 생성합니다.
    	m_pub = create_publisher<Twist>("skidbot/cmd_vel", 10);
    	m_sub = create_subscription<LaserScan>("skidbot/scan", 10,
                				std::bind(&ParkingNode::sub_callback, this, std::placeholders::_1));
  	}	
	
	// subscribe 시마다 실행될 callback.
	void sub_callback(const LaserScan::SharedPtr msg)//전방 장애물과의 거리를 laserscan으로 받은 뒤
	{
		auto forward_distance = (msg->ranges)[360];
			if (forward_distance > 0.8) { //0.8m 기준으로 정지와 계속 주행 여부 결정
   				move_robot(forward_distance); //계속 주행
    			} else {
      				stop_robot(); //주행 정지
				rclcpp::shutdown(); //rclcpp 종료
    			}
 	 }

	// 손쉬운 로봇제어를 위한 함수.
  	void move_robot(const float &forward_distance)
  	{
   		m_twist_msg.linear.x = 0.5; //전진속도
    		m_twist_msg.angular.z = 0.0; //각속도
    		m_pub->publish(m_twist_msg);

    		std::cout << "Distance from Obstacle ahead : " << forward_distance << std::endl;
  	}

 	 void stop_robot()
  	{
   		m_twist_msg.linear.x = 0.0;
   		m_twist_msg.angular.z = 0.0;
    		m_pub->publish(m_twist_msg);

    		RCLCPP_WARN(get_logger(), "Stop Robot and make Node FREE!");
  	}
};
