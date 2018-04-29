import plotly.plotly as py
import plotly.graph_objs as go
import learn

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

    num_minutes = 2
    NUM_FRAMES_TO_PLOT = int((num_minutes * 1000) / 40.0)

    print("Prepping data for plot.")

    X, y = learn.load_data([trial], regression=False)
    y_predicted = model.predict(X)
    print_stats(y, y_predicted)

    red_led = []
    ir_led = []
    for row in X:
        red = row[int((len(row)/2) - 1)]
        ir = row[-1]
        red_led.append(red)
        ir_led.append(ir)

    red_led = red_led[0:NUM_FRAMES_TO_PLOT]
    ir_led = ir_led[0:NUM_FRAMES_TO_PLOT]
    y = y[0:NUM_FRAMES_TO_PLOT]
    y_predicted = y_predicted[0:NUM_FRAMES_TO_PLOT]

    text = []
    for y_true, y_pred in zip(y, y_predicted):
        y_true = "Reliable" if y_true else "Unreliable"
        y_pred = "Reliable" if y_pred else "Unreliable"
        text.append("Reading: " + y_true + ", Prediction: " + y_pred)

    trace_red = go.Scatter(
        name='Red LED',
        y=red_led,
        mode='lines+markers',
        text=text,
        hoverinfo='text',
        marker=dict(
            color='red'
        ),
        line=dict(
            shape='spline'
        )
    )

    trace_ir = go.Scatter(
        name='IR LED',
        y=ir_led,
        mode='lines+markers',
        text=text,
        hoverinfo='text',
        marker=dict(
            color='blue'
        ),
        line=dict(
            shape='spline'
        )
    )

    data = [trace_red, trace_ir]

    layout = go.Layout(
        xaxis=dict(
            autorange=True,
            range=[0, 10],
            rangeslider=dict(autorange=True, range=[0, 10])
        )
    )

    filename = str(trial) + "-" + model.__class__.__name__

    print("Sending Plot to server")
    py.iplot(data, filename=filename, layout=layout)
    print("Plot created.")