from example_interfaces.srv import AddTwoInts

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class pad_cmd_vel(Node):

    def __init__(self):
        super().__init__('pad_cmd_vel')
        self.sub = self.create_subscription(Joy, '/joy', self.pad_cmd_vel_callback,10)
        self.pub = self.create_publisher(Twist,'/cmd_vel_joy',10)

        self.vel = Twist() 
        self.vel.linear.x = 0.0
        self.vel.linear.y = 0.0
        self.vel.angular.z = 0.0

        self.max_linear_speed = 2.0  # 最大直進速度
        self.max_angular_speed = 5.0  # 最大回転速度

        #パラメータ
        self.declare_parameter('deadzone', 0.1)

        self.deadzone = self.get_parameter('deadzone').value

    def apply_deadzone(self, value):
        if abs(value) < self.deadzone:
            return 0.0
        return value
    

    def pad_cmd_vel_callback(self, msg):
        self.vel.linear.x = self.apply_deadzone(msg.axes[1]) * self.max_linear_speed #直進方向（前方方向が正）
        self.vel.linear.y = self.apply_deadzone(msg.axes[0]) * self.max_linear_speed #横方向　（左が正）
        self.vel.angular.z= self.apply_deadzone(msg.axes[3]) * self.max_angular_speed #回転方向　（反時計ガ性）

        self.pub.publish(self.vel) 
        self.get_logger().info(f'Lx={self.vel.linear.x} Ly={self.vel.linear.y} Az={self.vel.angular.z}')


def main():
    rclpy.init()

    node = pad_cmd_vel()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
