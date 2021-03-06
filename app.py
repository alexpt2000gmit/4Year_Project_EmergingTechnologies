# Alexander Souza - G00317835
# 03/11/7017

#http://flask.pocoo.org/
#Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions
from flask import Flask, render_template, request

import numpy as np

import re
import base64
from scipy.misc import imread, imresize
import tensorflow as tf

# https://keras.io/
# https://keras.io/#getting-started-30-seconds-to-keras
# https://machinelearningmastery.com/handwritten-digit-recognition-using-convolutional-neural-networks-python-keras/

#Keras is a high-level neural networks API, written in Python and capable of running on top of TensorFlow, CNTK, or Theano. 
#It was developed with a focus on enabling fast experimentation. Being able to go from idea to result with the least possible 
#delay is key to doing good research.
import keras.models
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.applications.mobilenet import MobileNet

import sys 
import os


app = Flask(__name__)
global model, graph


def init():
    num_classes = 10
    img_rows, img_cols = 28, 28
    input_shape = (img_rows, img_cols, 1)

    #Ref: https://keras.io/getting-started/faq/
    # Ref: https://keras.io/getting-started/sequential-model-guide/
    model = Sequential()

    # in the first layer, you must specify the expected input data shape:
    # here, 20-dimensional vectors.
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    # Ref. https://keras.io/getting-started/faq/
    # load weights from first model; will only affect the first layer, dense_1.
    #Assuming you have code for instantiating your model, you can then load the weights you saved into a model with the same architecture:
    
    # Train File
    # To generate this file if nescessary, open the folder train and run the file cnn.py
    model.load_weights("cnn.h5")

    model.compile(loss=keras.losses.categorical_crossentropy, optimizer=keras.optimizers.Adadelta(), metrics=['accuracy'])
    graph = tf.get_default_graph()

    return model, graph


model, graph = init()

# Maping the index.html as main page
# The index is locate into template folder, default folder for Flask    
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ImageResult/', methods=['GET','POST'])
def predict():

    # Parse the image into the folder before read
    parseImage(request.get_data())

    # Read the Image on folder
    x = imread('static/ImageResult.png', mode='L')

    # Converting the image before predict
    x = np.invert(x)
    x = imresize(x,(28,28))
    x = x.reshape(1,28,28,1)

    with graph.as_default():
        # Predict the image, base on model added
        out = model.predict(x)

        # Print the result int screen
        print(np.argmax(out))

        # Return the result to HTML
        response = np.array_str(np.argmax(out))

        return response 

# Parse Image   
def parseImage(imgData):
    imgstr = re.search(b'base64,(.*)', imgData).group(1)
    with open('static/ImageResult.png','wb') as output:
        output.write(base64.decodebytes(imgstr))

# run the app and assigne the port 1111
if __name__ == '__main__':
    app.debug = True
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 1111))
    app.run(host='0.0.0.0', port=port)