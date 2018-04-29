import keys
import datetime
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import *
from sklearn.model_selection import cross_val_score, cross_val_predict, GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from sklearn.ensemble import *
from sklearn.utils import shuffle
from sklearn.preprocessing import scale

WINDOW_SIZE = 1  # Seconds

PICKLED_MODEL = 'cache/model.pickle'


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
        label = truth.df.loc[i:window_end, keys.O2].iloc[-1]
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
        actual = truth.df.loc[i:window_end, keys.O2].iloc[-1]
        expected = sensor.df.loc[i:window_end, keys.O2].iloc[-1]
        is_valid = (abs(actual - expected) <= 1)
        y.append(is_valid)
    return np.array(y)


def get_scores(models, X, y):
    for model in models:
        name = str(model.__class__.__name__)
        scores = cross_val_score(model, X, y, n_jobs=8, cv=10)
        print(name + " score : " + str(sum(scores)/len(scores)))
        y_pred = cross_val_predict(model, X, y, n_jobs=8, cv=10)
        print("True Label Count")
        count_labels(y)
        print("Predicted Label Count")
        count_labels(y_pred)
        print(classification_report(y, y_pred))



def visualize_regression(models, X, y):
    for model in models:
        name = str(model.__class__.__name__)
        y_predicted = cross_val_predict(model, X, y, n_jobs=8, cv=8)
        plt.figure()
        plt.plot(y, label="Actual")
        plt.plot(y_predicted, label="Predicted")
        plt.title(name)
        plt.legend()
        plt.show()


def count_labels(y):
    unique, counts = np.unique(y, return_counts=True)
    x = dict(zip(unique, counts))
    print("Labels Counts: " + str(x))


def load_data(trials, regression=False):
    X = None
    y = None
    pickle_name = '-'.join([str(trial.start_date) for trial in trials])
    pickle_name = 'cache/learn-' + pickle_name + str(regression) + "-" + str(WINDOW_SIZE)

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
        X, y = shuffle(X, y, random_state=42)
        X = scale(X)
        print("Pickling data.")
        pickle.dump((X, y), open(pickle_name, 'wb'))
    return X, y


def run_regression(trials):
    X, y = load_data(trials, regression=True)
    models = [LinearRegression(normalize=True), Ridge(normalize=True),
              RandomForestRegressor()]
    visualize_regression(models, X, y)
    get_scores(models, X, y)


def run_classifiers(trials):
    X, y = load_data(trials, False)
    print("Tuning Classifiers")
    models = []

    rf_params = {'n_estimators': range(1, 20), 'criterion': ['gini','entropy']}
    rf_optimal = _tune_classifier(RandomForestClassifier(), rf_params, X, y)
    models.append(RandomForestClassifier(**rf_optimal))

    # svm_params = {'C': [0.001, 0.01, 0.1, 1, 10], 'gamma': [0.001, 0.01, 0.1, 1]}
    # svm_optimal = _tune_classifier(SVC(), svm_params, X, y)
    # models.append(SVC())
    #
    # lr_params = {'penalty': ['l1', 'l2']}
    # lr_optimal = _tune_classifier(LogisticRegression(), lr_params, X, y)
    # models.append(LogisticRegression(**lr_optimal))

    count_labels(y)

    get_scores(models, X, y)


def pickle_model(trials):
    X, y = load_data(trials, False)
    print("Creating optimal Random Forest Model")
    count_labels(y)
    rf_params = {'n_estimators': range(5, 30), 'criterion': ['entropy']}
    rf_optimal = _tune_classifier(RandomForestClassifier(), rf_params, X, y)
    model = RandomForestClassifier(**rf_optimal)
    print("Scoring model")
    get_scores([model], X, y)
    print("Fitting model")
    model.fit(X, y)
    print("Pickling model")
    pickle.dump(model, open(PICKLED_MODEL, 'wb'))
    print("Done.")


def _tune_classifier(cls, params, X, y):
    name = str(cls.__class__.__name__)
    clf = GridSearchCV(cls, params, n_jobs=8, verbose=2)
    print("Brute forcing " + name + " Params...")
    clf.fit(X, y)
    print("Best parameters set found on development set:")
    print(clf.best_params_)
    return clf.best_params_
