import keys
import datetime
import numpy as np
from sklearn.linear_model import *
from sklearn.model_selection import cross_val_score, train_test_split



WINDOW_SIZE = 4  # Seconds


def prepare_data(truth, sensor):
    end = sensor.df.index.max()
    X = []
    y = []
    window_range = datetime.timedelta(seconds=WINDOW_SIZE)
    for i in sensor.df.index:
        window_end = i + window_range
        if window_end > end:
            break
        data = sensor.df[i:window_end]
        features = data[keys.RED_LED].append(data[keys.IR_LED]).tolist()
        X.append(features)
        label = truth.df.loc[i:window_end, keys.O2].mean()
        y.append(label)
    return np.array(X), np.array(y)


def run(trials):
    X = None
    y = None
    for trial in trials:
        print("Prepping data for trial: " + str(trial))
        truth = trial.get_ground_truth()
        sensor = trial.get_flora()
        _X, _y = prepare_data(truth, sensor)
        if X is None:
            X, y = _X, _y
        else:
            X = np.concatenate([X, _X])
            y = np.concatenate([y, _y])

    models = [LinearRegression(),
              Ridge(),
              Lasso()]
    for model in models:
        print("Analyzing :" + str(model.__class__.__name__))
        scores = cross_val_score(model, X, y, n_jobs=8)
        print(scores)

