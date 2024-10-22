//모든 Node는 포인터 형식.
//shared_ptr을 사용해 메모리 누수를 막기 위해 파생된 모든 데이터 추적
// Node 타입은 실제로는 std::shared_ptr<rclcpp::Node>형식
// 이는 rclcpp::Node::SharedPtr 형태를 갖음

#include "rclcpp/rclcpp.hpp"

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("simple_node");

  RCLCPP_INFO(node->get_logger(), "Logger Test");

  rclcpp::shutdown();
  return 0;
}
