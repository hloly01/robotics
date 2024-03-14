# robotics
ME 35 w/ Briana Bouchard 2023

Code written for a create3 robot. 

spinTime.py accepts linear and rotational commands from an airtable so that the robot can be driven remotely. 

training_test.py is the structure of the code used to navigate a maze, but is easier to troubleshoot as it does not include the nodes necessary for moving the robot

RotateAngle.py is the code used for the robot to drive autonomously through a maze and identify objects using code from teachable machine. 

labels.txt and keras_model.h5 are the models downloaded from teachable machine that allow our robot to recognize the 8 objects it was trained on. These files are referenced by both training_test.py and RotateAngle.py so need to be downloaded to the correct directory for those files to run. 
