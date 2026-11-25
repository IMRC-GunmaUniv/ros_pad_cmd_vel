from example_interfaces.srv import AddTwoInts

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class pad_cmd_vel(Node):

    def __init__(self):
        super().__init__('pad_cmd_vel')
        self.sub = self.create_subscription(Joy, '/joy', self.pad_cmd_vel_callback,10)
        self.pub = self.create_publisher(Twist,'/cmd_vel_pad',10)

        self.vel = Twist() 
        self.vel.linear.x = 0.0
        self.vel.linear.y = 0.0
        self.vel.angular.z = 0.0

        #パラメータ
        self.declare_parameter('deadzone', 0.1)
        self.declare_parameter('use_trapezoidal', True)
        self.declare_parameter('linear_acc', 2.0)
        self.declare_parameter('angular_acc', 4.0)

        self.deadzone = self.get_parameter('deadzone').value
        self.use_trapezoidal = self.get_parameter('use_trapezoidal').value
        self.linear_acc  = self.get_parameter('linear_acc').value
        self.angular_acc = self.get_parameter('angular_acc').value

    def apply_deadzone(self, value):
        if abs(value) < self.deadzone:
            return 0.0
        return value
    
    def calc_trapezoidal_velocity(self, target_velocity, current_velocity, acceleration):
        if target_velocity > current_velocity:
            current_velocity += acceleration
            if current_velocity > target_velocity:
                current_velocity = target_velocity
        elif target_velocity < current_velocity:
            current_velocity -= acceleration
            if current_velocity < target_velocity:
                current_velocity = target_velocity
        return current_velocity

    def pad_cmd_vel_callback(self, msg):
        if(self.use_trapezoidal):
            #台形加速処理
            self.vel.linear.x = self.calc_trapezoidal_velocity(self.apply_deadzone(msg.axes[1]) , self.vel.linear.x,  self.linear_acc)
            self.vel.linear.y = self.calc_trapezoidal_velocity(self.apply_deadzone(msg.axes[0]) , self.vel.linear.y,  self.linear_acc)
            self.vel.angular.z = self.calc_trapezoidal_velocity(self.apply_deadzone(msg.axes[3]), self.vel.angular.z, self.angular_acc)
        else:
            self.vel.linear.x = self.apply_deadzone(msg.axes[1]) #直進方向（前方方向が正）
            self.vel.linear.y = self.apply_deadzone(msg.axes[0]) #横方向　（左が正）
            self.vel.angular.z= self.apply_deadzone(msg.axes[3]) #回転方向　（反時計ガ性）

        self.pub.publish(self.vel) 
        self.get_logger().info(f'Lx={self.vel.linear.x} Ly={self.vel.linear.y} Az={self.vel.angular.z}')


def main():
    rclpy.init()

    node = pad_cmd_vel()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
