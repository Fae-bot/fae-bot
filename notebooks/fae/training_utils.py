from keras.callbacks import Callback
import time
import keras.models
import fae.dataset_loader
import pickle


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

    def start_timer(self):
        self.start_ts = time.time()

    def on_epoch_end(self, epoch, logs={}):
        logs['timestamp'] = time.time()-self.start_ts
        self.exp_log.append(logs)


class Experiment:
    def __init__(self, model, optimizer, fit_params, compile_params, data_loader, save_dir="./experiments/"):
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

    def run(self, display=-1, save=True):
        self.model.compile(optimizer=self.optimizer, **self.compile_params)
        kwargs = self.fit_params
        kwargs["callbacks"] = kwargs.get('callbacks', [])+[self.el]
        if display>0:
            kwargs["callbacks"].append(NBatchLogger(display=display))
        self.el.start_timer()
        self.model.fit(x=self.inputs, y=self.outputs, **kwargs)
        if save:
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
        pickle.dump(info, open(self.save_name, "wb"))
        return
