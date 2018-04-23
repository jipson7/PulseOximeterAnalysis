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


def prompt_for_action():
    action = input("Would you like to analyze (a) or delete (d) this trial? : ")
    action = action.strip()
    if action == 'a':
        return "ANALYZE"
    elif action == 'd':
        confirmation = input("If you're sure, type DELETE: ")
        if confirmation.strip().upper() == "DELETE":
            return "DELETE"
    print("Invalid input")
    exit(0)


if __name__ == "__main__":
    trials = fetch_trials()
    if len(trials) > 1:
        trial = prompt_for_trial(trials)
    elif len(trials) == 1:
        trial = trials[0]
    else:
        print("No trials to analyze")
        exit(0)

    print("Selected: " + str(trial))

    action = prompt_for_action()

    if action == "ANALYZE":
        trial.load()
        print("\nAnalyzing Trial: " + str(trial))
        analysis.graph_trial(trial)
        analysis.print_correlations(trial)
        analysis.print_errors(trial)
        analysis.print_stats(trial)
    elif action == "DELETE":
        trial.delete()



