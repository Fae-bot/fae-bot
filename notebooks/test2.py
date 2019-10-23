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

e=Experiment.from_file("experiments/exp_20191022_23-33-26.pickle")
e.run(display=1)
