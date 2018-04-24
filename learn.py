
sample_window_size = 100


def create_samples(trial):
    truth = None
    sensor = None
    for device in trial.devices:
        if device.name == 'USBUART':
            truth = device.df
        elif device.name == 'Flora':
            sensor = device.df
        else:
            raise Exception('Unknown device detected.')
    if truth is None or sensor is None:
        raise Exception('Devices incorrectly set.')
    print(truth.shape)