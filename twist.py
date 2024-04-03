import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
import cv2
from irobot_create_msgs.action import RotateAngle
from geometry_msgs.msg import Twist
import numpy as np
from collections import Counter
import time
import requests
import json

# Put the URL for your Airtable Base here
URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive' # Format: 'https://api.airtable.com/v0/BaseID/tableName
# Format: {'Authorization':'Bearer Access_Token'}
Headers = {'Authorization':'Bearer patnz4q3YD2b6QE5b.c888c6f15cb3bbb30c73cb0bcd9b186c09f7459d2e0569c8f80a34dd45a8651b'}

# Define the class DockActionClient as a subclass of Node
class RotateAngleClient(Node):

    # Define a function to initalize the node
    def __init__(self):
        super().__init__('rotate_angle_action_client') # Initialize a node the name dock_action_client
        
        # Create an action client using the action type 'RotateAngle' that we imported above 
        # with the action name 'rotate_angle' which can be found by running ros2 action list -t
        self._action_client = ActionClient(self, RotateAngle, 'rotate_angle')
        # initalize publisher to drive
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.arrived = {
            "fields": {
                "Arrived at station": 1
            }
        }
        self.reset = {
            "fields": {
                "Done": 0
            }
        }
        self.coffee_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recY2LOdyKyHehK5Y'
        self.latte_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recSIyskVTknipb5f'
        self.design_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recJQILiP3Ls6Cy5G'
        self.start_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recTkUKHYPDy8FoCc'
        self.customer_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recPm6ye2Mu5fELGP'
        timer_period = 1 # set timer 
        #creates timer that triggers a callback function
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0 # initialize timer to be zero

    def timer_callback(self):
        msg = Twist() # Assigns message type "Twist" that has been imported from the std_msgs module above
        msg.linear.x = .1
        self.publisher.publish(msg) # Publishes `msg` to topic 
        self.get_logger().info('Publishing: "%s"' % msg.linear.x) # Prints `msg.data` to console 
        self.process_and_respond() # go back to processing and respond
    # Define a function to send the goal to the action server which is already
    # running on the Create 3 robot. Since this action does not require any request value
    # as part of the goal message, the only argument of this function is self. 
    # For more details on this action, review  
    # https://github.com/iRobotEducation/irobot_create_msgs/blob/humble/action/Dock.action
    def send_goal(self, angle):

        # Create a variable for the goal request message to be sent to the action server
        goal_msg = RotateAngle.Goal()
        goal_msg.angle = (-3.1415*angle/180)
        goal_msg.max_rotation_speed = .1               

        # Instruct the action client to wait for the action server to become available
        self._action_client.wait_for_server()

        # Sends goal request to the server, returns a future object to the _send_goal_future
        # attribute of the class, and creates a feedback callback as a new function which
        # we will define below as 'feedback_callback' 
        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        # Creates a callback that executes a new function 'goal_response_callback'
        # when the future is complete. This function is defined below.
        # This happens when the action server accepts or rejects the request
        self._send_goal_future.add_done_callback(self.goal_response_callback)
        self.process_and_respond()
    
    # Define a response callback for when the future is complete. This will 
    # tell us if the goal request has been accepted or rejected by the server.
    # Note that because we have a future object we need to pass that in as 
    # an argument of this function.
    def goal_response_callback(self, future):

        # Store the result of the future as a new variable named 'goal_handle'
        goal_handle = future.result()

        # Perform a check to see if the goal was accepted or rejected and print to the logger.
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return
        self.get_logger().info('Goal accepted :)')

        # Now that we know the goal was accepted and we should expect a result,
        # ask for that result and return a future when received. 
        self._get_result_future = goal_handle.get_result_async()

        # Creates a callback that executes a new function 'get_result_callback'
        # when the future is complete. This function is defined below.
        # This happens when the action server accepts or rejects the request
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    # Define a result callback for when the future is complete. This will 
    # tell us the result sent to us from the server.
    # Note that because we have a future object we need to pass that in as 
    # an argument of this function.
    def get_result_callback(self, future):

        # Store the result from the server in a 'result' variable
        result = future.result().result

        # Print the result to the logger. We know what to ask for 'result.is_docked'
        # based on the action documentation for the dock action
        self.get_logger().info('Result: {0}'.format(result.pose))
        # Shut down rclpy
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback: {0}'.format(feedback.remaining_angle_travel))

    
    def process_and_respond(self):
        while True:
            angle = 70 # currently arbitrary guess at spacing between sections
            r = requests.get(url = URL, headers = Headers, params = {})
            data = r.json()
            # print(data)
            # putting data into dictonaries by subteam
            airtable_names = {
                (data['records'][0]['fields']['Name']), (data['records'][1]['fields']['Name']), 
                (data['records'][2]['fields']['Name']), (data['records'][3]['fields']['Name']),
                (data['records'][4]['fields']['Name'])
            }
            design_info = {
                'design':   data['records'][0]['fields']['Design choice'],
                'arrived':  data['records'][0]['fields']['Arrived at station'], 
                'done':     data['records'][0]['fields']['Done']
            }
            customer_info = {
                'design':   data['records'][0]['fields']['Design choice'],
                'arrived':  data['records'][1]['fields']['Arrived at station'], 
                'done':     data['records'][1]['fields']['Done'],
                'name':     data['records'][1]['fields']['Customer Name']
            }
            latte_info = {
                'arrived':  data['records'][2]['fields']['Arrived at station'], 
                'done':     data['records'][2]['fields']['Done']
            }
            coffee_info = {
                'arrived':  data['records'][4]['fields']['Arrived at station'], 
                'done':     data['records'][4]['fields']['Done']
            }
            start_info = {
                'cup':      data['records'][3]['fields']['Arrived at station'],
                'done':     data['records'][3]['fields']['Done']
            }
            # input for transport team
            if start_info['cup'] == 1:
                # insert some sort of zeroing here
                print("place cup")
            if start_info['done'] == 1: # cup placed, go to coffee
                print('go to coffee station')
                # go to coffee
                response = requests.patch(self.start_URL, json=self.reset, headers=Headers)
                response = requests.patch(self.coffee_URL, json=self.arrived, headers=Headers)
                self.send_goal(angle)
            if coffee_info['done'] == 1:
                print("go to milk station")
                response = requests.patch(self.coffee_URL, json=self.reset, headers=Headers)
                response = requests.patch(self.latte_URL, json=self.arrived, headers=Headers)
                self.send_goal(angle)
            if latte_info['done'] == 1: 
                print("go to design station")
                response = requests.patch(self.latte_URL, json=self.reset, headers=Headers)
                response = requests.patch(self.design_URL, json=self.arrived, headers=Headers)
                self.send_goal(angle)
            if design_info['done'] == 1: 
                print("deliver to customer")
                response = requests.patch(self.design_URL, json=self.reset, headers=Headers)
                response = requests.patch(self.customer_URL, json=self.arrived, headers=Headers)
                self.send_goal(angle)
            if customer_info['done'] == 1:
                print("show tip screen")
            # Listen to the keyboard for presses. 27 is the ASCII for the esc key on your keyboard.
            keyboard_input = cv2.waitKey(1)
            if keyboard_input == 27:
                break

def main(args=None):
    rclpy.init(args=args)
    rotate_class = RotateAngleClient() # making an instance of rotateangle
    rotate_class.process_and_respond()
    rclpy.spin(rotate_class)

if __name__ == '__main__':
    main()