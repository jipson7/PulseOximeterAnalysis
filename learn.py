
sample_window_size = 100


def run(trial):
    truth = trial.get_ground_truth()
    sensor = trial.get_flora()
    print(truth.df.shape)
    print(sensor.df.shape)