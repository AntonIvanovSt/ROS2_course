#include "rclcpp/rclcpp.hpp"
#include "speed_interfaces/srv/set_speed.hpp"

class SpeedService : public rclcpp::Node {
  public:
    SpeedService() : Node("speed_service") {
        service_ = this->create_service<speed_interfaces::srv::SetSpeed>(
            "set_speed",
            std::bind(&SpeedService::handle_request, this,
                      std::placeholders::_1, std::placeholders::_2));
    }

  private:
    void handle_request(
        const std::shared_ptr<speed_interfaces::srv::SetSpeed::Request> request,
        std::shared_ptr<speed_interfaces::srv::SetSpeed::Response> response) {
        // Просто установим скорость и отправим успешный ответ
        response->success = true;
        response->message = "Speed set to " + std::to_string(request->speed);
        RCLCPP_INFO(this->get_logger(), "Setting speed: %f", request->speed);
    }

    rclcpp::Service<speed_interfaces::srv::SetSpeed>::SharedPtr service_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SpeedService>());
    rclcpp::shutdown();
    return 0;
}
