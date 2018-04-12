from data import Loader


def prompt_for_trial(trials):
    print("Select one of the following trials:")
    for i, trial in enumerate(trials):
        print(str(i) + ") " + str(trial))
    selection = input("Enter a numer: ")
    try:
        return trials[int(selection)]
    except IndexError as e:
        print(e)


if __name__ == "__main__":
    loader = Loader()
    trials = loader.fetch_trials()
    trial = prompt_for_trial(trials)
    devices = trial.get_devices()
    for device in devices:
        print(device)
