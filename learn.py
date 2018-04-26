import keys
import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
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


def run(trial):
    truth = trial.get_ground_truth()
    sensor = trial.get_flora()
    X, y = prepare_data(truth, sensor)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_predicted = model.predict(X_test)
    print(y_predicted)
    for j, k in zip(y_predicted, y_test):
        print("Predicted: " + str(int(round(j))) + ", Actual: " + str(int(round(k))))
