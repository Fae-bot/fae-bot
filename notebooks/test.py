import logging, os

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import warnings
warnings.catch_warnings()
warnings.filterwarnings("ignore",category=FutureWarning)

from fae import dataset_loader
from fae.training_utils import Experiment, NBatchLogger

import numpy as np
import tensorflow as tf

import keras

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.regularizers import l2
from keras.optimizers import Adam, SGD
from keras import backend as K


dropout=0.1
core_size=128

model = Sequential()
model.add(Dense(core_size, activation='sigmoid', input_shape=(14,)))
model.add(Dropout(dropout))
model.add(Dense(core_size, activation='sigmoid'))
model.add(Dropout(dropout))
model.add(Dense(core_size, activation='sigmoid'))
model.add(Dropout(dropout))
model.add(Dense(core_size, activation='sigmoid'))
model.add(Dropout(dropout))
model.add(Dense(4, activation='linear'))

opt = Adam(lr=0.004, amsgrad=True)


e=Experiment(model=model, optimizer=opt, 
             fit_params = { 'batch_size':10000,
                            'epochs':50,
                            'verbose':0,
                            'shuffle':True,
                            'validation_split':0.1,
                            'callbacks':[NBatchLogger(display=10)]},
            compile_params={'loss'    :'mean_squared_error',
                            'metrics' :['mean_squared_error']},
            data_loader = 'fae.dataset_loader.load_dataset("../datasets/real/2019-10-18/raw/")[2:4]')

e.run()
