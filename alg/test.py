import ray
import numpy as np
from tensorflow.keras import models,layers
from tensorflow.keras import utils as np_utils
from pyjava.api.mlsql import PythonContext,RayContext
import mock
import os
import numpy as np
from pyjava import rayfix

ray_context = RayContext.connect(globals(),None)
conf = ray_context.conf()
home = conf["HOME"]

## rebuild model from data lake
model_path = os.path.join(home,"tmp","minist_model7")   
model_servers = RayContext.parse_servers(conf["modelServers"])
ray_context.fetch_as_dir(model_path,model_servers)
model = models.load_model(model_path)

## get data  and use model to predict
temp_data = [item for item in RayContext.collect()]
train_images = np.array([np.array(item["image"]) for item in temp_data])
train_labels = np_utils.to_categorical(np.array([item["label"] for item in temp_data]))
train_images = train_images.reshape((len(temp_data),28*28))
predictions = model.predict(train_images)
result = [{"actualCol":a,"predictCol":b} for (a,b) in zip(predictions,train_labels)]
context.build_result(result)

