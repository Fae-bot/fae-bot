from keras.models import load_model
import numpy as np


class InferenceModel:
    def __init__(self, filename, insize=10, outsize=4):
        self.model = load_model(filename)
        self.input_scale_factors = [np.array([0.0]*insize), np.array([1.0]*insize)]
        self.output_scale_factors = [np.array([0.0]*outsize), np.array([1.0]*outsize)]

    def inference(self, ins):
        norm_ins = (ins-self.input_scale_factors[0])/self.input_scale_factors[1]
        norm_outs = self.model.predict(norm_ins)[0]
        outs = norm_outs * self.output_scale_factors[1] + self.output_scale_factors[0]
        return outs
