from data import fetch_trials
import analysis
import learn
import pickle


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
                   "(v) visualize the applied model, \n"
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
    elif action == 'v':
        return 'VISUALIZE'
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
        learning_trials = [trial]
        selection = input("Select other trials to include in training (numeric values separated by spaces): ")
        indices = [int(x) for x in selection.split()]
        for i in indices:
            learning_trials.append(trials[i])

        for t in learning_trials:
            t.load()

        reg = input("Regression (r) or classification (c)? ")
        if reg.strip().lower() == 'r':
            learn.run_regression(learning_trials)
        else:
            analyze = input("Would you like to \n"
                            "(c) compare models, \n"
                            "(p) or pickle for testing? ")
            if analyze.strip().lower() == 'c':
                learn.run_classifiers(learning_trials)
            else:
                learn.pickle_model(learning_trials)
    elif action == 'CREATE':
        trial.load()
        filename = './data.csv'
        trial.dump_csv(filename)
    elif action == "TRACE":
        trial.load()
        analysis.graph_led_traces(trial.get_flora())
    elif action == "VISUALIZE":
        trial.load()
        try:
            model = pickle.load(open(learn.PICKLED_MODEL, 'rb'))
        except FileNotFoundError:
            print("Must pickle a model before visualizing. Run learning directive.")
        from visualize import visualize_model_predictions
        visualize_model_predictions(model, trial)




