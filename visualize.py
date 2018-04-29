import learn
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report


def print_stats(y_true, y_pred):
    print("True label counts")
    learn.count_labels(y_true)

    print("Predicted label counts")
    learn.count_labels(y_pred)

    print("Accuracy of prediction: " + str(accuracy_score(y_true, y_pred)))

    print("Classification Report")
    print(classification_report(y_true, y_pred))


def visualize_model_predictions(model, trial):

    print("Prepping data for plot.")

    X, y = learn.load_data([trial], regression=False)
    y_predicted = model.predict(X)
    print_stats(y, y_predicted)

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

