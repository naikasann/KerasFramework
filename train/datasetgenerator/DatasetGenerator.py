import keras
from keras.preprocessing.image import img_to_array, load_img
from keras.utils import to_categorical

import numpy as np
import os

class DatasetGenerator:
    # initial function
    def __init__(self):
        self.reset()
    
    # Empty the images list & labels list.
    def reset(self):
        self.images = []
        self.labels = []

    # count the number of data.
    def text_datacounter(self,datapath):
        # open resorse.
        with open(datapath) as f:
            readlines = f.readlines()
        return len(readlines)
    
    # Generator to read text.
    def text_dataset_generator(self, resourcepath, input_shape, classes, batchsize):
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
                except Exception as e:
                    print("Failed to load data.")
                    print("ERROR : ", e)
                    exit(1)
                 # Normalize image.
                image /= 255.0
                # list append.
                self.images.append(image)
                self.labels.append(to_categorical(linebuffer[1], len(classes)))

                # When the batch size is reached, it yields.
                if(len(self.images) == batchsize):
                    inputs = np.asarray(self.images, dtype = np.float32)
                    targets = np.asarray(self.labels, dtype = np.float32)
                    self.reset()

                    yield inputs, targets

    # count the number of data.
    def folder_datacounter(self, datapath):
        image_list = os.listdir(datapath)
        return len(image_list)

    # Generator to read folder.
    def folder_dataset_generator(self, resourcepath, input_shape, classes, batchsize):
        # Refers to all the contents of a folder. (Assign a list of image paths.)
        image_list = os.listdir(resourcepath)
        while True:
            for image_path in image_list:
                image_path = os.path.join(resourcepath, image_path)
                try:
                    # I'll load the image, and if it doesn't work, I'll terminate the program.
                    image = img_to_array(load_img(image_path, target_size=input_shape))
                except Exception as e:
                    print("Failed to load data.")
                    print("ERROR : ", e)
                    exit(1)
                # Normalize image.
                image /= 255
                # list append.
                self.images.append(image)

                # Labeling based on the name of the image and the name of the category.
                for count, category in enumerate(classes):
                    if category in image_path:
                        self.labels.append(to_categorical(count, len(classes)))
                        append = True
                        break
                # Check the success of the label assignment.
                if not append:
                    print("Failed to assign a label.")
                    exit(1)
                else:
                    append = False

                # When the batch size is reached, it yields.
                if(len(self.images) == batchsize):
                    inputs = np.asarray(self.images, dtype = np.float32)
                    targets = np.asarray(self.labels, dtype = np.float32)
                    self.reset()

                    yield inputs, targets