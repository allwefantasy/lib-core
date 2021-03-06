from keras.datasets import mnist
import mock
if "context" not in globals() and "context" not in locals():
    context = mock.Mock()    

(train_images,train_labels),(test_images,test_labels) = mnist.load_data()
images = train_images.reshape((train_images.shape[0],28*28))
result = [{"image":image.tolist(),"label":int(label)} for (image,label) in  zip(images,train_labels)]
context.build_result(result)
