
sample_window_size = 100


def create_samples(trial):
    truth = trial.get_ground_truth()
    sensor = trial.get_flora()
    print(truth.shape)