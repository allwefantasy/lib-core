import ray
from tensorflow.keras import models,layers
from tensorflow.keras import utils as np_utils
from pyjava.api.mlsql import PythonContext,RayContext
import mock
import os
import numpy as np
from pyjava import rayfix


is_mock = "context" not in globals() and "context" not in locals()
enable_ray = not is_mock and "rayAddress" in context.conf
home = "/" if is_mock else context.conf["HOME"]

if not is_mock:
    ray_address = None if not enable_ray else context.conf["rayAddress"]
    ray_context = RayContext.connect(globals(),ray_address)
    data_servers = ray_context.data_servers()
else:
    context = mock.Mock() 
    ray.util.connect(conn_str="192.168.31.207:10001")               

    

def data():
    if is_mock:        
        from tensorflow.keras.datasets import mnist
        (train_images,train_labels),(test_images,test_labels) = mnist.load_data()    
        train_images = train_images.reshape((60000,28*28))
        train_images = train_images.astype('float32')/255

        test_images = test_images.reshape((10000,28*28))
        test_images = test_images.astype('float32')/255

        train_labels = np_utils.to_categorical(train_labels)
        test_labels = np_utils.to_categorical(test_labels)
    else:
        temp_data = [item for item in RayContext.collect_from(data_servers)]
        train_images = np.array([np.array(item["image"]) for item in temp_data])
        train_labels = np_utils.to_categorical(np.array([item["label"] for item in temp_data])    )
        train_images = train_images.reshape((len(temp_data),28*28))
    return train_images,train_labels

@ray.remote
@rayfix.last
def train():
    train_images,train_labels = data()
    network = models.Sequential()
    network.add(layers.Dense(512,activation="relu",input_shape=(28*28,)))
    network.add(layers.Dense(10,activation="softmax"))
    network.compile(optimizer="rmsprop",loss="categorical_crossentropy",metrics=["accuracy"])
    network.fit(train_images,train_labels,epochs=6,batch_size=128)
    model_path = os.path.join(home,"tmp","minist_model")
    network.save(model_path)
    return os.path.join("tmp","minist_model")

if  is_mock:
    model_path = ray.get(train.remote())
else:
    model_path = ray.get(train.remote()) if enable_ray else train()

context.build_result([{"model":model_path}])
