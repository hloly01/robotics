# robotics
ME 35 w/ Briana Bouchard 2023

Code written for a create3 robot. 

DRIVING CREATE 3: 
- spinTime.py accepts linear and rotational commands from an airtable so that the robot can be driven remotely. 

NAVIGATING A MAZE:
- training_test.py is the structure of the code used to navigate a maze, but is easier to troubleshoot as it does not include the nodes necessary for moving the robot
- RotateAngle.py is the code used for the robot to drive autonomously through a maze and identify objects using code from teachable machine. 
- labels.txt and keras_model.h5 are the models downloaded from teachable machine that allow our robot to recognize the 8 objects it was trained on. These files are referenced by both training_test.py and RotateAngle.py so need to be downloaded to the correct directory for those files to run. 

LATTE MACHINE: 
- latte_airtable_test.py tested that the airtable values were being pulled correctly and that the rows were linked to the correct turning commands. This version excludes any actual spinning so that the code is not complicated by ROS. 
- twist.py and airtable_data.py control transport for the automated latte machine final project. airtable_data.py pulls and sorts data from the airtable. twist.py controls the spinning of the roomba and posts updates about its location to the airtable. 
