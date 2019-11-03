
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam, SGD


def model_v1():
    batch_size = 256
    num_output = 10
    epochs = 5
    rng_seed = 42

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


def make_dense_model(dropout=0.1,
               core_size=128,
               num_layers=4,
               activation='sigmoid',
               input_size=14,
               output_size=4):
    model = Sequential()
    for k in range(num_layers):
        if k==0:
            model.add(Dense(core_size,
                            activation=activation,
                            input_shape=(input_size,)))
        else:
            model.add(Dense(core_size,
                            activation=activation))
        if dropout>0:
            model.add(Dropout(dropout))
    model.add(Dense(output_size, activation='linear'))
    return model
