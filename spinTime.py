import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import requests 
import json 
import time


# Put the URL for your Airtable Base here
# Format: 'https://api.airtable.com/v0/BaseID/tableName
URL = 'https://api.airtable.com/v0/appAeIb5oKuvkT1ac/Drive'
# Format: {'Authorization':'Bearer Access_Token'}
Headers = {'Authorization':'Bearer patnz4q3YD2b6QE5b.beeeaeb07b2fda4b93c08c08471eaa0a57730327ce445ae66750e31f1cf5d71e'}

class MovementPublisher(Node):
    def __init__(self, initial_linear=None, initial_angular=None):
        super().__init__('movement_publisher')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

    def run(self, linear_speed, angular_speed):
        twist = Twist()
        r = requests.get(url = URL, headers = Headers, params = {})
        data = r.json()
        print('got requests')
        print(data)

        # make sure order of table hasn't been edited, if so edit number in data so that correct values are called
        check = ['Angular (1.0)', 'Linear (0.25)']
        airtable_names = [
            (data['records'][0]['fields']['Name']),
            (data['records'][1]['fields']['Name'])
        ]
        print("airtable names: ", airtable_names)
        if check == airtable_names:
            angular = data['records'][0]['fields']
            linear = data['records'][1]['fields']
            print('table in correct order!')
        else:
            print("Check that table order is correct. It should be: ", check)

        # assign linear and angular values if set to on, else set to zero
        if linear['On/Off'] == 1:
            linear_speed = float(linear['Value (0-1)'])
            # self.linear = linear_speed
        else:
            linear_speed = float(0)
            # self.linear = linear_speed
        print("linear speed: ", linear_speed)
        if angular['On/Off'] == 1:
            angular_speed  = float(angular['Value (0-1)'])
            # self.angular = angular_speed
        else:
            angular_speed = float(0)
            # self.angular = angular_speed
        print("angular speed: ", angular_speed)
        print('Driving the robot')
        twist.linear.x = linear_speed # input value with at least one decimal. optimal value ~ 0.25
        twist.angular.z = angular_speed # input value with at least one decimal. optimal value ~ 0.5
        self.publisher.publish(twist)
        return linear_speed, angular_speed


def main(args=None):
    rclpy.init(args=args)
    movement_publisher = MovementPublisher()  # Create instance of MovementPublisher
    # set initial values to 0
    linear_speed = 0
    angular_speed = 0
    try:
         while True:
            linear_speed, angular_speed = movement_publisher.run(linear_speed, angular_speed)
            time.sleep(.75)
    except KeyboardInterrupt:
        print('\nCaught Keyboard Interrupt')
    finally:
        movement_publisher.destroy_node()  # Cleanup the MovementPublisher node
        rclpy.shutdown()

if __name__ == '__main__':
    main()
