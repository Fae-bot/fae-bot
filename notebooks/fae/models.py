
import numpy as np
import tensorflow as tf

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.regularizers import l2
from keras.optimizers import Adam, SGD
from keras import backend as K


def model_v1():
    batch_size = 256
    num_output = 10
    epochs = 5
    rng_seed = 42





    """(x_train, y_train), (x_test, y_test) = mnist.load_data()

    x_train = x_train.reshape(60000, 784)
    x_test = x_test.reshape(10000, 784)
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    y_train = keras.utils.to_categorical(y_train, num_output)
    y_test = keras.utils.to_categorical(y_test, num_output)"""

    model = Sequential()
    model.add(Dense(32, activation='relu', input_shape=(11,)))
    #model.add(Dropout(0.2))
    model.add(Dense(32, activation='sigmoid', input_shape=(32,)))
    model.add(Dense(32, activation='relu', input_shape=(32,)))
    model.add(Dense(32, activation='sigmoid', input_shape=(32,)))
    model.add(Dense(32, activation='relu', input_shape=(32,)))
    model.add(Dense(32, activation='sigmoid', input_shape=(32,)))
    model.add(Dense(32, activation='relu', input_shape=(32,)))
    model.add(Dense(7, activation='linear'))

    model.summary()
    opt = SGD(lr=0.008, decay=1e-6, momentum=0.9, nesterov=True)
    #opt = Adam(lr=0.004, amsgrad=True)
    model.compile(loss='mean_squared_error',
      optimizer=opt,
      metrics=['accuracy'])

    model.fit(inputs, outputs,
        batch_size=10,
        epochs=20,
        verbose=2,
        shuffle=True,
        validation_split=0.0)

    #score = model.evaluate(x_test, y_test, verbose=0)
    #print('Test loss:', score[0])
    #print('Test accuracy:', score[1])











    #opt = SGD(lr=0.08, decay=1e-6, momentum=0.9, nesterov=True)
    opt = Adam(lr=0.004, amsgrad=True)
    model.compile(loss='mean_squared_error',
      optimizer=opt,
      metrics=['accuracy'])

    model.fit(inputs, outputs,
        batch_size=10,
        epochs=10000,
        verbose=2,
        shuffle=True)














    ax,ay,az = inputs[0][4:7]
    rx,ry,rz = outputs[0][4:7]
    x,y,z, = model.predict(np.array([inputs[0]]))[0][-3:]

    print((ax-x, ay-y,az-z))
    print((rx, ry,rz))
    print(x,y,z)
    print(ax,ay,az)
    print(rx,ry,rz)
    print(((rx-x)**2+(ry-y)**2+(rz-z)**2))
