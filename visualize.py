import learn
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error

def print_stats(y_true, y_pred):
    print("True label counts")
    learn.count_labels(y_true)

    print("Predicted label counts")
    learn.count_labels(y_pred)

    print("Accuracy of prediction: " + str(accuracy_score(y_true, y_pred)))

    print("Classification Report")
    print(classification_report(y_true, y_pred))


def visualize_classification_predictions(model, trial):

    print("Prepping data for plot.")

    X, y = learn.load_data([trial], regression=False)
    y_predicted = model.predict(X)

    if hasattr(model, 'feature_importance_'):
        print("Significant Features")
        feature_importances = np.array(model.feature_importances_)
        print("Num: " + str(len(feature_importances)))
        print("Mean: " + str(feature_importances.mean()))
        print("Std Deviation: " + str(feature_importances.std()))

    print_stats(y, y_predicted)

    prompt = input("Would you like to create traces images? (y or n) ")

    if prompt.strip().lower() != 'y':
        return

    file_num = 0
    root_folder = 'results/'

    for row, y_true, y_pred in zip(X, y, y_predicted):
        file_num += 1
        plt.figure()
        half = int(len(row) / 2)
        red_led = row[:half]
        ir_led = row[half:]
        plt.plot(red_led)
        plt.plot(ir_led)
        if y_pred and y_true:
            result_type = 'tp/'
        elif y_pred and not y_true:
            result_type = 'fp/'
        elif not y_pred and y_true:
            result_type = 'fn/'
        elif not y_pred and not y_true:
            result_type = 'tn/'
        filename = root_folder + result_type + str(file_num) + '.png'
        print("Creating image " + str(filename))
        plt.savefig(filename)


def visualize_regression_predictions(model, trial):
    print("Prepping data for plot.")
    name = str(model.__class__.__name__)
    X, y = learn.load_data([trial], regression=True)
    y_predicted = model.predict(X)
    rmse = math.sqrt(mean_squared_error(y, y_predicted))
    print(name + " RMSE: " + str(rmse))
    plt.figure()
    plt.plot(y[:200], label="Actual")
    plt.plot(y_predicted[:200], label="Predicted")
    plt.title(name)
    plt.legend()
    plt.show()