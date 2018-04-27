import keys
import datetime
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import *
from sklearn.model_selection import cross_val_score, cross_val_predict, GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import *

WINDOW_SIZE = 4  # Seconds

regression_models = [LinearRegression(normalize=True), Ridge(normalize=True),
                     RandomForestRegressor()]

classification_models = [LogisticRegression(), RandomForestClassifier(n_estimators=5, criterion='entropy')]


def prepare_data(sensor):
    end = sensor.df.index.max()
    X = []
    window_range = datetime.timedelta(seconds=WINDOW_SIZE)
    for i in sensor.df.index:
        window_end = i + window_range
        if window_end > end:
            break
        data = sensor.df[i:window_end]
        features = data[keys.RED_LED].append(data[keys.IR_LED]).tolist()
        X.append(features)
    return np.array(X)


def prepare_regression_labels(truth):
    end = truth.df.index.max()
    y = []
    window_range = datetime.timedelta(seconds=WINDOW_SIZE)
    for i in truth.df.index:
        window_end = i + window_range
        if window_end > end:
            break
        label = truth.df.loc[i:window_end, keys.O2].mean()
        y.append(label)
    return np.array(y)


def prepare_classification_labels(sensor, truth):
    end = truth.df.index.max()
    y = []
    window_range = datetime.timedelta(seconds=WINDOW_SIZE)
    for i in truth.df.index:
        window_end = i + window_range
        if window_end > end:
            break
        actual = truth.df.loc[i:window_end, keys.O2].mean()
        expected = sensor.df.loc[i:window_end, keys.O2].mean()
        is_valid = (abs(actual - expected) <= 1)
        y.append(is_valid)
    return np.array(y)


def get_scores(models, X, y):
    for model in models:
        name = str(model.__class__.__name__)
        print("Scoring :" + name)
        scores = cross_val_score(model, X, y, n_jobs=8)
        print(scores)


def plot_predictions(models, X, y):
    for model in models:
        name = str(model.__class__.__name__)
        y_predicted = cross_val_predict(model, X, y, n_jobs=8)
        plt.figure()
        plt.plot(y, label="Actual")
        plt.plot(y_predicted, label="Predicted")
        plt.title(name)
        plt.legend()
        plt.show()


def count_labels(y):
    unique, counts = np.unique(y, return_counts=True)
    x = dict(zip(unique, counts))
    print("Labels in classifier: " + str(x))


def load_data(trials, regression):
    X = None
    y = None
    pickle_name = '-'.join([str(trial.start_date) for trial in trials])
    pickle_name = 'cache/learn-' + pickle_name + str(regression)

    if os.path.isfile(pickle_name):
        print("Loading data from pickle")
        (X, y) = pickle.load(open(pickle_name, 'rb'))
    else:
        for trial in trials:
            print("Prepping data for trial: " + str(trial))
            truth = trial.get_ground_truth()
            sensor = trial.get_flora()
            _X = prepare_data(sensor)
            if regression:
                _y = prepare_regression_labels(truth)
            else:
                _y = prepare_classification_labels(sensor, truth)
            if X is None:
                X, y = _X, _y
            else:
                X = np.concatenate([X, _X])
                y = np.concatenate([y, _y])
        print("Pickling data.")
        pickle.dump((X, y), open(pickle_name, 'wb'))
    return X, y


def run_model_comparison(trials, regression=False):
    X, y = load_data(trials, regression)

    if regression:
        models = regression_models
        plot_predictions(models, X, y)
    else:
        models = classification_models
        count_labels(y)

    get_scores(models, X, y)


def tune_random_forest(trials):
    X, y = load_data(trials, False)
    params = {'n_estimators': range(1, 20), 'criterion': ['gini', 'entropy']}
    clf = GridSearchCV(RandomForestClassifier(), params, n_jobs=8, verbose=2)
    print("Brute forcing Random Forest Params...")
    clf.fit(X, y)
    print("Best parameters set found on development set:")
    print(clf.best_params_)


def tune_svm(trials):
    # TODO BROKEN
    X, y = load_data(trials, False)
    params = {'kernel': ['rbf', 'linear']}
    clf = GridSearchCV(SVC(), params, n_jobs=8, verbose=2)
    print("Brute forcing SVM Params...")
    clf.fit(X, y)
    print("Best parameters set found on development set:")
    print(clf.best_params_)
