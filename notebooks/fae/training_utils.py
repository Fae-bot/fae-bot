from keras.callbacks import Callback
import time
import random
import keras.models
import fae.dataset_loader
import pickle
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
import matplotlib.pyplot as plt

class NBatchLogger(Callback):
    """
    A Logger that prints last performance per `display` epochs.
    """
    def __init__(self, display):
        self.display = display
        self.metric_cache = {}

    def on_epoch_end(self, epoch, logs={}):
        if epoch == 0:
            return
        for k in self.params['metrics']:
            if k in logs:
                self.metric_cache[k] = logs[k]
        if epoch % self.display == 0:
            metrics_log = ''
            for (k, v) in self.metric_cache.items():
                val = v
                if abs(val) > 1e-3:
                    metrics_log += ' - %s: %.4f' % (k, val)
                else:
                    metrics_log += ' - %s: %.4e' % (k, val)
            print('Epoch: {}/{} ... {}'.format(epoch,
                                          self.params['epochs'],
                                          metrics_log))
            self.metric_cache.clear()


class ExperimentLogger(Callback):
    """
    A Logger that log average performance per `display` steps.
    """
    def __init__(self):
        self.exp_log = list()
        self.start_ts = time.time()

    def start_timer(self):
        self.start_ts = time.time()

    def on_epoch_end(self, epoch, logs={}):
        logs['timestamp'] = time.time()-self.start_ts
        self.exp_log.append(logs)


class Experiment:
    def __init__(self, model, optimizer, fit_params, compile_params, data_loader, save_dir="./experiments/", label=None):
        self.model_class = model.__class__.__module__ + "." + model.__class__.__name__
        self.model = eval(self.model_class).from_config(model.get_config())
        self.optimizer_class = optimizer.__class__.__module__ + "." + optimizer.__class__.__name__
        self.optimizer = eval(self.optimizer_class).from_config(optimizer.get_config())
        self.fit_params = fit_params
        self.compile_params = compile_params
        self.data_loader = data_loader
        (self.inputs, self.outputs) = eval(data_loader)
        self.el = ExperimentLogger()
        self.save_dir = save_dir
        self.save_name = None
        self.label = label

    @staticmethod
    def from_file(filename, save_dir="./experiments/"):
        info = pickle.load(open(filename, "rb"))
        model = eval(info['model_class']).from_config(info["model"])
        opt = eval(info['optimizer_class']).from_config(info["optimizer"])
        fp = dict(info["fit_params"])
        fp["callbacks"] = []

        return Experiment(
            model=model,
            optimizer=opt,
            fit_params=fp,
            compile_params=info["compile_params"],
            data_loader=info["data_loader"],
            save_dir=save_dir
        )

    def run(self, display=-1, save=False):
        self.model.compile(optimizer=self.optimizer, **self.compile_params)
        kwargs = self.fit_params
        #kwargs["callbacks"] = kwargs.get('callbacks', [])+[self.el]
        kwargs["callbacks"] = [self.el]
        if display > 0:
            kwargs["callbacks"].append(NBatchLogger(display=display))
        self.el.start_timer()
        self.model.fit(x=self.inputs, y=self.outputs, **kwargs)
        if save:
            self.write()

    def save(self):
        self.write()

    def write(self):
        info = dict()
        info['model'] = self.model.get_config()
        info['model_class'] = self.model_class
        info['optimizer'] = self.optimizer.get_config()
        info['optimizer_class'] = self.optimizer_class
        info['exp_log'] = self.el.exp_log
        info['compile_params'] = self.compile_params
        info['data_loader'] = self.data_loader
        fp = dict(self.fit_params)
        fp['callbacks'] = [str(type(x)) for x in fp.get('callbacks', [])]
        info['fit_params'] = fp
        self.save_name = self.save_dir+f"/exp_{time.strftime('%Y%m%d_%H-%M-%S')}.pickle"
        if self.label is None:
            self.label = self.save_name
        info["label"]=self.label
        pickle.dump(info, open(self.save_name, "wb"))
        return


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


class ExperimentSet:
    def __init__(self, params_set=None):
        if params_set is None:
            params_set = list()
        self.params_set = params_set
        self.experiments = list()

    def random_params(self, params_ranges, num_exp):
        for i in range(num_exp):
            params = dict()
            for k in params_ranges.keys():
                params[k] = random.choice(params_ranges[k])
            if params not in self.params_set:
                self.params_set.append(params)
        return self.params_set

    def create_experiments(self, fit_params, compile_params, data_loader, set_name="<ExperienceSet>", ):
        self.experiments = list()
        for ps in self.params_set:
            model = make_dense_model(**ps)
            label = set_name + " "
            for k, v in ps.items():
                if isinstance(v, float):
                    sv = f"{v:.2f}"
                else:
                    sv = str(v)
                label += k+"="+sv+" "
            e = Experiment(model=model, optimizer=Adam(lr=0.004, amsgrad=True),
                   fit_params=fit_params,
                   compile_params=compile_params,
                   data_loader=data_loader,
                   label=label)
            self.experiments.append(e)

    def run(self, display=100, save=True):
        for e in self.experiments:
            print("-" * 20)
            print(e.label)
            e.run(display=display, save=True)

    def plot(self, trim_left=0):
        series = list()
        for e in self.experiments:
            series.append((e.label,
                           [x['val_loss'] for x in e.el.exp_log[trim_left:]],
                           [x['timestamp'] for x in e.el.exp_log[trim_left:]]))
        fig, ax = plt.subplots()
        for s in series:
            ax.plot(s[2], s[1], label=s[0])
        legend = ax.legend(loc='upper center', shadow=True)





















