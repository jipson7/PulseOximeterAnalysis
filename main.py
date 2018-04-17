from data import fetch_trials
import analysis


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
    if len(trials) > 1:
        trial = prompt_for_trial(trials)
    elif len(trials) == 1:
        trial = trials[0]
    else:
        print("No trials to analyze")
        exit(0)
    trial.load()
    analysis.graph_trial(trial)



