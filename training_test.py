from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
from collections import Counter
import time
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)
# Load the model and labels
model = load_model("keras_model.h5", compile=False)
class_names = open("labels.txt", "r").readlines()
# dictionary for directions - input correct directions once determined
object_directions = {
    'Kiwi': 'left',
    'Elephant': 'left',
    'Bear': 'left',
    'Cube': 'left',
    'Vader': 'left',
    'Mug': 'left',
    'Mario': 'left',
    'Floor': 'straight' 
}
# write function defintions here
def identify(object_list):
    count_dict = Counter(object_list)
    most_common_object = count_dict.most_common(1)[0][0]
    return most_common_object, count_dict
'''
need turn right/left, and straight functions or something that accomplishes that
'''
# setup for picam
picam2 = Picamera2() # assigns camera variable
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous}) # sets auto focus mode
picam2.start() # activates camera
time.sleep(1) # wait for camera to start up
# initialize variables 
object_list = []
num_avg = 10
count_confirmed = []
while True:
    # Grab the picam's image.
    image = picam2.capture_array("main")
    # Discard alpha channel
    image_3_channel = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    # Resize the image
    image_resized = cv2.resize(image_3_channel, (224, 224), interpolation=cv2.INTER_AREA)
    # check image size is as expected 
    # Show the image in a window
    cv2.imshow("Picam Image", image)
    
    # Make the image a numpy array and reshape it to the models input shape.
    image = np.asarray(image_resized, dtype=np.float32).reshape(1, 224, 224, 3)
    # Normalize the image array
    image = (image / 127.5) - 1
    # Predicts the model
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    rounded_confidence_score = np.round(confidence_score * 100)
    # creates list of 10 most recent objects
    object_list.append(class_name[2:].rstrip('\n')) 
    # the rstrip gets rid of the /n and makes list compatible with dictionary
    if len(object_list) > num_avg:
        object_list.pop(0)    
    print("last ", num_avg, " objects: ", object_list)
    # Print prediction and confidence score
    print("Object:", class_name[2:])
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    # run function to identify most common objevy
    most_common_object, count_dict = identify(object_list)
    print("count: ", count_dict[most_common_object])
    print("must be greater than: ", np.round(.9*num_avg))
    '''
    CHANGE CONFIDENCE VALUE IN IF STATEMENT!!! (currently 68)
    # can also tune value for average check (currently .9)
    '''
    # statement to check that object is confirmed 
    if count_dict[most_common_object] > (np.round(.9*num_avg)) and rounded_confidence_score > 68: 
        object_confirmed = True
    else: 
        object_confirmed = False
    print("object confirmed", object_confirmed)
    count_confirmed.append(object_confirmed)
    if len(count_confirmed) > 2:
        count_confirmed.pop(0)  
    confirmed_num = Counter(count_confirmed)    
    print("count confirmed: ", count_confirmed)
    print("confirmed_num: ", confirmed_num[True])

    if object_confirmed and confirmed_num[True] != 2:
        print("go straight")
    elif object_confirmed and confirmed_num[True] == 2: # and 6 inches away [INSERT CODE HERE]
        print("its time to turn")
        direction = object_directions[most_common_object]
        if direction == 'right': 
            print('turning right')
            # code to turn right
        elif direction == 'left': 
            print('turning left')
            # code to turn left
        elif direction == 'straight':
            print('go straight')
                # code to go straight
        else:
            print('something weird is happening, check directions')
    else: 
        print('go straight')
        # code to go straight
    # Listen to the keyboard for presses.
    keyboard_input = cv2.waitKey(1)
    # 27 is the ASCII for the esc key on your keyboard.
    if keyboard_input == 27:
        break
picam2.release()
cv2.destroyAllWindows()