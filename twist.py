# code for transport team. Tells roomba to turn and updates airtable when arrived
# ask Hannah for questions about code
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
from airtable_data import airtable

# Put the URL for your Airtable Base here
URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive' # Format: 'https://api.airtable.com/v0/BaseID/tableName
# Format: {'Authorization':'Bearer Access_Token'}
Headers = {'Authorization':'Bearer patnz4q3YD2b6QE5b.c888c6f15cb3bbb30c73cb0bcd9b186c09f7459d2e0569c8f80a34dd45a8651b'}

# Define the class DockActionClient as a subclass of Node
class RotateAngleClient(Node):

    # Define a function to initalize the node
    def __init__(self):
        super().__init__('rotate_angle_action_client') # Initialize a node the name dock_action_client
        self._action_client = ActionClient(self, RotateAngle, 'rotate_angle')
        # intialize lists and dictionaries 
        self.recent_orders = ['test', 'test']
        self.queue = []
        self.first_instance_queue = True
        self.first_instance = True
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
        self.reset_start = {
            "fields": {
                "Arrived at station": 0
            }
        }
        self.URl = ''
        self.coffee_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recY2LOdyKyHehK5Y'
        self.latte_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recSIyskVTknipb5f'
        self.design_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recJQILiP3Ls6Cy5G'
        self.start_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recTkUKHYPDy8FoCc'
        self.customer_URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recPm6ye2Mu5fELGP'
        # list of all airtable rows to be updated
        self.patch_all = [self.coffee_URL, self.latte_URL, self.design_URL, self.start_URL, self.customer_URL]
        # set all values to 0 when started
        for url in self.patch_all:
            response = requests.patch(url, json=self.reset, headers=Headers)
            response = requests.patch(url, json=self.reset_start, headers=Headers)
    # ROS stuff
    def send_goal(self, angle):
        # Create a variable for the goal request message to be sent to the action server
        goal_msg = RotateAngle.Goal()
        goal_msg.angle = (-3.1415*angle/180)
        goal_msg.max_rotation_speed = .1               

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)
    # more ROS stuff
    def goal_response_callback(self, future):
        goal_handle = future.result()
        # Perform a check to see if the goal was accepted or rejected and print to the logger.
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return
        self.get_logger().info('Goal accepted :)')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    # callbacks and ROS stuff
    # when the roomba arrives, update airtable value to 1
    def get_result_callback(self, future):
        result = future.result().result
        # if successful, value goes to 1
        if result: 
            response = requests.patch(self.URL, json=self.arrived, headers=Headers)
        self.get_logger().info('Result: {0}'.format(result.pose))
        self.process_and_respond() # go back to while loop (processing and respond)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback: {0}'.format(feedback.remaining_angle_travel))

    def process_and_respond(self):
        while True:
            angle = 71.75 # spacing between sections
            [design_info, customer_info, customer_order, 
            latte_info, coffee_info, start_info, all_zeros] = airtable() # update airtable values

            # reset arrived value if changed in line 169
            if self.arrived['fields']['Arrived at station'] == 0:
                self.arrived['fields']['Arrived at station'] = 1

            # making queue based on user input design orders 
            self.recent_orders.append(customer_order['fields']['Design']) # append customer order to list
            if len(self.recent_orders) > 1: # if the list is longer than 2, delete the oldest value
                self.recent_orders.pop(0) 

            # if the recent_orders list has two differnt orders, add most recent to queue 
            if self.recent_orders[0] != self.recent_orders[1]: 
                self.queue.append(self.recent_orders[1])
            print("queue: ", self.queue)
            if len(self.queue)>0 and self.first_instance_queue == True:
                self.queue.pop(0)
                self.first_instance_queue = False

            # if there is no order being made and someone places an order, start
            if len(self.queue) > 0 and all_zeros: 
                response = requests.patch(self.start_URL, json=self.arrived, headers=Headers)
                print('oh hell nah')

            ''' TRANSPORT TEAM LOGIC THAT CONTORLS SPINNING ACTION '''
            # first instance is necessary because the airtable value does not get immediately overwritten
            # to allow for multiple teams to read value & start processes
            if start_info['cup'] == 1 and self.first_instance == True: # if started place cup
                self.first_instance = False
                response = requests.patch(self.design_URL, json={"fields": {"Design": self.queue[0]}}, headers=Headers)
            if start_info['done'] == 1: # cup placed, go to coffee station
                print('go to coffee station')
                # go to coffee
                response = requests.patch(self.start_URL, json=self.reset_start, headers=Headers)
                response = requests.patch(self.start_URL, json=self.reset, headers=Headers)
                self.reset_start['fields']['Arrived at station'] = 0
                self.URL = self.coffee_URL
                self.send_goal(angle)
                break # break while loop to start spinning
            if coffee_info['done'] == 1: # coffee done, go to milk station
                print("go to milk station")
                response = requests.patch(self.coffee_URL, json=self.reset_start, headers=Headers)
                response = requests.patch(self.coffee_URL, json=self.reset, headers=Headers)
                self.URL = self.latte_URL
                self.send_goal(angle)
                break # break while loop to start spinning
            if latte_info['done'] == 1: # milk done, go to design station
                print("go to design station")
                response = requests.patch(self.latte_URL, json=self.reset_start, headers=Headers)
                response = requests.patch(self.latte_URL, json=self.reset, headers=Headers)
                self.URL = self.design_URL
                self.send_goal(angle)
                break # break while loop to start spinning
            if design_info['done'] == 1: # design done, go to customer
                print("deliver to customer")
                response = requests.patch(self.design_URL, json=self.reset_start, headers=Headers)
                response = requests.patch(self.design_URL, json=self.reset, headers=Headers)
                self.URL = self.customer_URL
                self.send_goal(angle)
                break # break while loop to start spinning

            # if at customer station and cup has been taken, go back to cup station for new order
            if customer_info['done'] == 1 and customer_info['arrived'] ==1: 
                if len(self.queue) > 0:
                    self.queue.pop(0)
                self.URL = self.start_URL
                self.first_instance = True
                response = requests.patch(self.customer_URL, json=self.reset_start, headers=Headers)
                response = requests.patch(self.customer_URL, json=self.reset, headers=Headers)
                if len(self.queue) > 0: # if theres a queue, start a new order
                    self.send_goal(angle*2)
                    break # break while loop to start spinning
                else:
                    self.arrived['fields']['Arrived at station'] = 0 # if no queue, do nothing  #just changed the 1 to a 0
                    self.send_goal(angle*2)
                    #send goal to 
                    break # break while loop to start spinning
                   
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
