from data import Loader
import matplotlib.pyplot as plt


def prompt_for_trial(trials):
    print("Select one of the following trials:")
    for i, trial in enumerate(trials):
        print(str(i) + ") " + str(trial))
    #selection = input("Enter a number: ")
    selection = 0
    try:
        return trials[int(selection)]
    except IndexError as e:
        print(e)




if __name__ == "__main__":
    loader = Loader()
    trials = loader.get_trials()
    trial = prompt_for_trial(trials)
    devices = trial.get_devices()
    plt.figure()
    for device in devices:
        df = device.get_dataframe()
        df.plot.line()
    plt.show()
