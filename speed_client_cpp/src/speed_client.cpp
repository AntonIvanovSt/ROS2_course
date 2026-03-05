#include "rclcpp/rclcpp.hpp"
#include "speed_interfaces/srv/set_speed.hpp"

class SpeedClient : public rclcpp::Node {
  public:
    SpeedClient() : Node("speed_client") {
        client_ =
            this->create_client<speed_interfaces::srv::SetSpeed>("set_speed");

        while (!client_->wait_for_service(std::chrono::seconds(1))) {
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(this->get_logger(),
                             "Interrupted while waiting for service. Exiting.");
                return;
            }
            RCLCPP_INFO(this->get_logger(),
                        "Waiting for service to be available...");
        }
    }

    void send_request(double speed) {
        auto request =
            std::make_shared<speed_interfaces::srv::SetSpeed::Request>();
        request->speed = speed;

        auto result = client_->async_send_request(request);
        if (rclcpp::spin_until_future_complete(shared_from_this(), result) ==
            rclcpp::FutureReturnCode::SUCCESS) {
            RCLCPP_INFO(this->get_logger(), "Service response: %s",
                        result.get()->message.c_str());
        } else {
            RCLCPP_ERROR(this->get_logger(),
                         "Failed to call service set_speed");
        }
    }

  private:
    rclcpp::Client<speed_interfaces::srv::SetSpeed>::SharedPtr client_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto client_node = std::make_shared<SpeedClient>();
    client_node->send_request(
        1.5); // Отправляем запрос на установку скорости 1.5
    rclcpp::shutdown();
    return 0;
}
