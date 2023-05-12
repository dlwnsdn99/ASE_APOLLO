#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

//using을 사용하면 컴파일러에서 LaserScan이 sensor_msgs::msg::LaserScan로 사용되는걸 알림
//본문은 이거임 rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr m_sub;

using LaserScan = sensor_msgs::msg::LaserScan;

class LaserSub : public rclcpp::Node {
private:
	//using으로 대체 가능하다는데
	//using LaserScan = sensor_msgs::msg::LaserScan; 이건가?
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr m_sub;

public:
  LaserSub() : Node("topic_sub_oop_node") {
		// timer 생성시 std::bind 사용
		// 익명함수로 대체 가능. 
		// using 쓰면 this->LaseScan으로 바꿀 수 있는건가?
    m_sub = this->create_subscription<sensor_msgs::msg::LaserScan>(
        "skidbot/scan", 10,
        std::bind(&LaserSub::sub_callback, this, std::placeholders::_1));
  }
	//subscribe시마다 동작할 callback
	//들어오는 데이터 : SharedPtr 형식
  void sub_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
    // std::cout << (msg->ranges).size() << std::endl;

    // for (auto e : msg->ranges)
    //   std::cout << e << std::endl;

    RCLCPP_INFO(this->get_logger(), "Distance from Front Object : %f", (msg->ranges)[360]);
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  //subscriber는 반드시 spin을 통한 갱신이 있어야 최신 메시지 수신이 가능하다.
  rclcpp::spin(std::make_shared<LaserSub>());
  rclcpp::shutdown();

  return 0;
}
