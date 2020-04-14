import keras
from keras.preprocessing.image import img_to_array, load_img
from keras.utils import to_categorical

import numpy as np

class DatasetGenerator:
    # initial function
    def __init__(self):
        self.reset()
    
    # Empty the images list & labels list.
    def reset(self):
        self.images = []
        self.labels = []
    
    # Generator to read text.
    def text_dataset_generator(self, yml):
        # Read the information you need from YAML.
        resourcepath = yaml["Resourcedata"]["resourcepath"]
        input_shape = (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"])
        classes = yml["Resorsedata"]["classes"]

        # open resorse.
        with open(resourcepath) as f:
            readlines = f.readlines()

        # loop for generator.
        while True:
            for line in readlines:
                # ["image path" "label"] => linebuffer 
                linebuffer = line.split(" ")
                try:
                    # I'll load the image, and if it doesn't work, I'll terminate the program.
                    image = img_to_array(load_img(linebuffer[0], target_size=input_shape))
                    # Normalize image.
                    image /= 255.0
                except Exception as e:
                    print("Failed to load data.")
                    exit(1)
                
                # list append.
                self.images.append(image)
                self.labels.append(to_categorical(linebuffer[1], len(classes)))

                # When the batch size is reached, it yields.
                if(len(x_data) == yml["Trainsetting"]["batchsize"]):
                    inputs = np.asarray(self.images, dtype = np.float32)
                    targets = np.asarray(self.labels, dtype = np.float32)
                    self.reset()

                    yield inputs, targets
