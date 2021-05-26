from tensorflow.keras import models,layers
from tensorflow.keras import utils as np_utils
from pyjava.api.mlsql import RayContext
import os
import numpy as np

ray_context = RayContext.connect(globals(),None)
data_servers = ray_context.data_servers()

def data():
    temp_data = [item for item in RayContext.collect_from(data_servers)]
    train_images = np.array([np.array(item["image"]) for item in temp_data])
    train_labels = np_utils.to_categorical(np.array([item["label"] for item in temp_data])    )
    train_images = train_images.reshape((len(temp_data),28*28))
    return train_images,train_labels

def train():
    train_images,train_labels = data()
    network = models.Sequential()
    network.add(layers.Dense(512,activation="relu",input_shape=(28*28,)))
    network.add(layers.Dense(10,activation="softmax"))
    network.compile(optimizer="rmsprop",loss="categorical_crossentropy",metrics=["accuracy"])
    network.fit(train_images,train_labels,epochs=6,batch_size=128)
    model_path = os.path.join("tmp","minist_model")
    network.save(model_path)
    return model_path
  
model_path = train()
ray_context.build_result_from_dir(model_path)