from data import fetch_trials
import matplotlib.pyplot as plt


def prompt_for_trial(trials):
    print("Select one of the following trials:")
    for i, trial in enumerate(trials):
        print(str(i) + ") " + str(trial))
    selection = input("Enter a number: ")
    try:
        return trials[int(selection)]
    except IndexError as e:
        print(e)


if __name__ == "__main__":
    trials = fetch_trials()
    trial = prompt_for_trial(trials)
    trial.load()
    for device in trial.devices:
        print(device.df.head(50))

