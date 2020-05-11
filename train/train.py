import tensorflow as tf
from tensorflow.python.client import device_lib

import keras
from keras import optimizers
from keras.models import Model
from keras.models import load_model
from keras.callbacks import ModelCheckpoint, TensorBoard

import numpy as np
import datetime as dt
import os
import h5py
import yaml
import shutil
import matplotlib.pyplot as plt
# Self-made dataset lib
from datasetgenerator.DatasetGenerator import DatasetGenerator
from mymodel.MyModel import MyModel

#--------------------< function >--------------------
# Check to see if you have a folder, and if you don't, create a folder.
def makedir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

# Checking the status of the GPU
def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    dev_list = [x.name for x in local_device_protos if x.device_type == 'GPU']
    if dev_list is None:
        return False
    return True

def write_graph(history, write_enable, datetime, validation = False):
    # Draw and save the accuracy graph.
    plt.figure(figsize=(6,4))
    plt.plot(history.history['acc'])
    plt.title('accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    if validation:
        plt.plot(history.history['val_acc'])
        plt.legend(['traindata', 'validata'], loc='upper left')
    else:
        plt.legend(['traindata'], loc='upper left')
    if write_enable:
        plt.show()
    plt.savefig("./result/" + datetime +"/" + "accuracy.png")

    # Draw and save the loss graph.
    plt.figure(figsize=(6,4))
    plt.plot(history.history['loss'])
    plt.title('loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    if validation:
        plt.plot(history.history['val_loss'])
        plt.legend(['traindata', 'valdata'], loc='upper left')
    else:
        plt.legend(['traindata'], loc='upper left')
    if write_enable:
        plt.show()
    plt.savefig("./result/" + datetime +"/loss.png")
#----------------------------------------------------

#--------------------< main sequence >--------------------
def main():
    print("######################################")
    print("# Keras Framework. Training program. #")
    print("#      Final Update Date : 2020/4/21 #")
    print("######################################")

    # open congig yaml file.
    print("open config file...")
    with open("config.yaml") as file:
        print("complete!")
        yml = yaml.safe_load(file)

    # GPU checking.
    print("GPU use option checking...")
    if yml["running"]["GPU"]:
        print("use gpu. setting...")
        # if GPU setting.
        if not get_available_gpus():
            print("GPU is not available.You should review your configuration files and GPU preferences.")
            exit(1)
        # GPU setting
        gpu_config = tf.ConfigProto(allow_soft_placement=True)
        gpu_config.gpu_options.allow_growth = True
        keras.backend.set_session(tf.Session(config=gpu_config))
    else:
        # It warns you not to use the GPU.
        print("gpu dont use. It does not use a GPU. It takes a lot of time. Are you ready? (y/n)")
        text = input()
        if text == "y" or text == "Y":
            print("ok. It will be executed as it is.")
        else:
            print("ok. You should review your configuration files and GPU preferences.")
            exit(0)

    # Store the execution time in a variable.
    execute_time = dt.datetime.now().strftime("%m_%d_%H_%M")
    makedir("result/")
    makedir("result/" + execute_time)
    makedir("result/" + execute_time + "/model")
    # Copy the YAML file that contains the execution environment.
    shutil.copy("config.yaml", "result/" + execute_time)

    # Dataset Generator loadding.
    dataset = DatasetGenerator()
    print("dataset generator loading...")
    print("--------- dataset ---------")
    if yml["CNN_type"] == "category" or yml["CNN_type"] == "label":
        if yml["Resourcedata"]["readdata"] == "text" or yml["Resourcedata"]["readdata"] == "TEXT":
            generator = dataset.text_dataset_generator( yml["Resourcedata"]["resourcepath"],
                                                        (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                        yml["Resourcedata"]["classes"],
                                                        yml["Trainsetting"]["batchsize"])
            datacount = dataset.text_datacounter(yml["Resourcedata"]["resourcepath"])
        elif yml["Resourcedata"]["readdata"] == "onefolder" or yml["Resourcedata"]["readdata"] == "Onefolder":
            generator = dataset.onefolder_dataset_generator(yml["Resourcedata"]["resourcepath"],
                                                        (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                        yml["Resourcedata"]["classes"],
                                                        yml["Trainsetting"]["batchsize"])
            datacount = dataset.onefolder_datacounter(yml["Resourcedata"]["resourcepath"])
        elif yml["Resourcedata"]["readdata"] == "folder" or yml["Resourcedata"]["readdata"] == "Folder":
            generator = dataset.folder_dataset_generator(yml["Resourcedata"]["resourcepath"],
                                                        (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                        yml["Resourcedata"]["classes"],
                                                        yml["Trainsetting"]["batchsize"])
            datacount = dataset.folder_datacounter(yml["Resourcedata"]["resourcepath"])
        else:
            print("It seems to have selected an unspecified generator. Stops the program.")
            exit(1)
        print("traindata : ", datacount)  
    elif yml["CNN_type"] == "segmentation" or yml["CNN_type"] == "image":
        generator = dataset.segmentation_generator(yml["Resourcedata"]["resourcepath"],
                                                        yml["Segmentationpath"]["targetpath"],
                                                        (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                        yml["Resourcedata"]["classes"],
                                                        yml["Trainsetting"]["batchsize"])
        datacount, targetcount = dataset.segmentation_datacounter(yml["Resourcedata"]["resourcepath"], yml["Segmentationpath"]["targetpath"])
        print("input count", datacount)
        print("target count", targetcount)
    else:
        print("It seems to have selected an unspecified generator. Stops the program.")

    # Validation setting.
    print("Validation use...?  : ", yml["Validation"]["Usedata"])
    if yml["Validation"]["Usedata"]:
        # use validation data.
        val_dataset = DatasetGenerator()
        print("Create a generator to use the validation.")
        if yml["CNN_type"] == "category" or yml["CNN_type"] == "label":
            if yml["Validation"]["readdata"] == "text" or yml["Validation"]["readdata"] == "TEXT":
                val_generator = val_dataset.text_dataset_generator(yml["Validation"]["resourcepath"],
                                                            (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                            yml["Resourcedata"]["classes"],
                                                            yml["Trainsetting"]["batchsize"]
                                                            )
                val_datacount = val_dataset.text_datacounter(yml["Validation"]["resourcepath"])
            elif yml["Validation"]["readdata"] == "onefolder" or yml["Validation"]["readdata"] == "Onefolder":
                val_generator = val_dataset.onefolder_dataset_generator(yml["Validation"]["resourcepath"],
                                                            (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                            yml["Resourcedata"]["classes"],
                                                            yml["Trainsetting"]["batchsize"]
                                                            )
                val_datacount = val_dataset.onefolder_datacounter(yml["Validation"]["resourcepath"])
            elif yml["Validation"]["readdata"] == "folder" or yml["Validation"]["readdata"] == "Folder":
                val_generator = val_dataset.folder_dataset_generator(yml["Validation"]["resourcepath"],
                                                            (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                            yml["Resourcedata"]["classes"],
                                                            yml["Trainsetting"]["batchsize"]
                                                            )
                val_datacount = val_dataset.folder_datacounter(yml["Validation"]["resourcepath"])
            else:
                print("It seems to have selected an unspecified generator. Stops the program.")
                exit(1)
            print("validation data : ", val_datacount)
        elif yml["CNN_type"] == "segmentation" or yml["CNN_type"] == "image":
            val_generator = val_dataset.segmentation_generator(yml["Validation"]["resourcepath"],
                                                        yml["Segmentationpath"]["valtargetpath"],
                                                        (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"]),
                                                        yml["Resourcedata"]["classes"],
                                                        yml["Trainsetting"]["batchsize"])
            val_datacount, targetcount = val_dataset.segmentation_datacounter(yml["Validation"]["resourcepath"], yml["Segmentationpath"]["valtargetpath"])
            print("input count", datacount)
            print("target count", targetcount)
    else:
        # dont use validation data. Continue learning.
        print("It does not use any validation.")
    print("---------------------------")

    # Model loading.
    mymodel = MyModel(yml["Modelsetting"]["optimizers"],
                      yml["Modelsetting"]["model_loss"],
                      yml["Trainsetting"]["learnrate"])
    if yml["Modelsetting"]["retrain_model"]:
        model = mymodel.load_model(yml["Modelsetting"]["model_path"],
                                   yml["Modelsetting"]["weight_path"],
                                   yml["Modelsetting"]["trainable"])
    else:
        input_shape = (yml["Resourcedata"]["img_row"], yml["Resourcedata"]["img_col"], 3)
        model = mymodel.create_model(yml["Modelsetting"]["network_architecture"],
                                     input_shape, 
                                     yml["Resourcedata"]["classes"],
                                     yml["Modelsetting"]["trainable"])
    
    # callback function(tensorboard, modelcheckpoint) setting.
    # first modelcheckpoint setting.
    modelCheckpoint = ModelCheckpoint(filepath = "./result/"+ execute_time + "/model/" + yml["Trainingresult"]["model_name"] +"_{epoch:02d}.h5",
                                  monitor=yml["callback"]["monitor"],
                                  verbose=yml["callback"]["verbose"],
                                  save_best_only=yml["callback"]["save_best_only"],
                                  save_weights_only=yml["callback"]["save_weights_only"],
                                  mode=yml["callback"]["mode"],
                                  period=yml["callback"]["period"])

    # next tensorboard setting.
    tensorboard = TensorBoard(log_dir = yml["callback"]["tensorboard"], histogram_freq=yml["callback"]["tb_epoch"])
    
    # training!
    if not yml["Validation"]["Usedata"]:
        # no validation
        history = model.fit_generator(
            generator = generator,
            steps_per_epoch = int(np.ceil(datacount / yml["Trainsetting"]["batchsize"])),
            epochs = yml["Trainsetting"]["epoch"],
            callbacks=[modelCheckpoint]
        )
    else:
        #validation
        history = model.fit_generator(
            generator = generator,
            steps_per_epoch = int(np.ceil(datacount / yml["Trainsetting"]["batchsize"])),
            epochs = yml["Trainsetting"]["epoch"],
            validation_data = val_generator,
            validation_steps = int(np.ceil(val_datacount / yml["Trainsetting"]["batchsize"])),
            callbacks=[modelCheckpoint]
        )

    # save weights and model.
    model.save_weights("./result/" + execute_time + "/model/" + yml["Trainingresult"]["model_name"] + "_end_epoch" + ".h5")
    # write network architecture.
    f = open("./result/" + execute_time + "/model/model_architecture.yaml", "w")
    f.write(yaml.dump(model.to_yaml()))
    f.close()
    # result graph write.
    write_graph(history, yml["Trainingresult"]["graph_write"], execute_time, yml["Validation"]["Usedata"])
#---------------------------------------------------------

if __name__ == "__main__":
    main()