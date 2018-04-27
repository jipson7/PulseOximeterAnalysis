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
    action = input("Would you like to \n"
                   "(a) analyze the data, \n"
                   "(l) run learning algorithm, \n"
                   "(c) create a csv, \n"
                   "(t) view led traces, \n"
                   "(d) or delete this trial? ")
    action = action.strip()
    if action == 'a':
        return "ANALYZE"
    elif action == 'd':
        confirmation = input("If you're sure, type DELETE: ")
        if confirmation.strip().upper() == "DELETE":
            return "DELETE"
    elif action == 'l':
        return 'LEARN'
    elif action == 'c':
        return 'CREATE'
    elif action == 't':
        return 'TRACE'
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
    elif action == 'LEARN':
        combine = input("Combine data from all trials to train? (y), (n)")
        if combine.strip().lower() == 'y':
            # Custom selection of trials
            learning_trials = trials[2:]
        else:
            learning_trials = [trial]
        import learn
        for t in learning_trials:
            t.load()
        reg = input("Regression (r) or classification (c)? ")
        if reg.strip().lower() == 'r':
            learn.run_model_comparison(learning_trials, regression=True)
        else:
            #TODO Remove
            learn.tune_svm(learning_trials)
            #learn.tune_random_forest(learning_trials)
            #learn.run_model_comparison(learning_trials)
    elif action == 'CREATE':
        trial.load()
        filename = './data.csv'
        trial.dump_csv(filename)
    elif action == "TRACE":
        trial.load()
        analysis.graph_led_traces(trial.get_flora())




