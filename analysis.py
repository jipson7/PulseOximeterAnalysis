import matplotlib.pyplot as plt
import numpy as np
import time
import keys
import math


hr_styles = ['r--', 'r-.', 'r:', 'r-']
oxygen_styles = ['k--', 'k-.', 'k:', 'k-']


def graph_dfs(data_frames):
    """Graphs a list of data frames"""
    ax = data_frames[0].plot()
    for df in data_frames[1:]:
        df.plot(ax=ax, kind="line")
    plt.show()


def graph_led_traces(device, full_trace=False, same_graph=True):

    red_trace = device.df[keys.RED_LED]
    ir_trace = device.df[keys.IR_LED]
    if not full_trace:
        # 500 frames = 20 seconds
        red_trace = red_trace.iloc[0:500]
        ir_trace = ir_trace.iloc[0:500]
    red_trace.plot(title="Red LED")

    if same_graph:
        ir_trace.plot(title="RED and IR LED")
    else:
        plt.figure()
        ir_trace.plot(title="IR LED")
    plt.show()


def graph_trial(trial):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    for device in trial.devices:
        df = prune_first_rows(device.df)
        x_axis = df.index.values
        hr_values = df[keys.HR]
        oxygen_values = df[keys.O2]
        ax1.plot(x_axis, oxygen_values, oxygen_styles.pop(), label='O2 - ' + str(device))
        ax2.plot(x_axis, hr_values, hr_styles.pop(), label='HR - ' + str(device))

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=8)

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Oxygen Saturation (%)")
    ax1.set_ylim(bottom=70)
    ax1.tick_params(axis='x', rotation=80)
    ax2.set_ylabel("Heart-Rate (BPM)", color='r')
    ax2.tick_params('y', colors='r')
    ax2.set_ylim(bottom=0)
    plt.savefig('./report/images/raw/trial-' + str(trial.description) + '-plot-' + str(time.time()) + '.png')
    plt.show()


def print_correlations(trial):
    for d1, d2 in trial.device_combinations():
        df1 = d1.df
        df2 = d2.df
        method = 'pearson'
        o2_corr = df1[keys.O2].corr(df2[keys.O2], method=method)
        hr_corr = df1[keys.HR].corr(df2[keys.HR], method=method)
        print("\nAnalyzing Device Correlations: ")
        print("(" + str(d1) + ") <=> (" + str(d2) + ")")
        print("O2 Correlation (" + method + ") = " + str(o2_corr))
        print("HR Correlation (" + method + ") = " + str(hr_corr))


def print_errors(trial):
    hr_errors = []
    o2_errors = []

    df1 = trial.devices[0].df
    df2 = trial.devices[1].df

    n = df1.shape[0]

    print("\nAnalyzing Device Errors: ")
    print("(" + str(trial.devices[0]) + ") <=> (" + str(trial.devices[1]) + ")")
    for index, row in df1.iterrows():
        data1 = row
        data2 = df2.loc[index]
        hr_1, hr_2 = data1[keys.HR], data2[keys.HR]
        o2_1, o2_2 = data1[keys.O2], data2[keys.O2]
        hr_errors.append(hr_1 - hr_2)
        o2_errors.append(o2_1 - o2_2)
    hr_rmse = math.sqrt(sum([x ** 2.0 for x in hr_errors]) / n)
    o2_rmse = math.sqrt(sum([x ** 2.0 for x in o2_errors]) / n)
    print("RMSE HR: " + str(hr_rmse))
    print("RMSE O2: " + str(o2_rmse))
    hr_mae = sum([abs(x) for x in hr_errors]) / n
    o2_mae = sum([abs(x) for x in o2_errors]) / n
    print("MAE HR: " + str(hr_mae))
    print("MAE O2: " + str(o2_mae))


def print_stats(trial):
    for device in trial.devices:
        hr = device.df[keys.HR]
        o2 = device.df[keys.O2]
        print("\n" + str(device) + " Stats: ")
        print("HR Mean:    " + str(round(hr.mean(), 2)))
        print("HR Std Dev: " + str(round(hr.std(), 2)))
        print("O2 Mean:    " + str(round(o2.mean(), 2)))
        print("O2 Std Dev: " + str(round(o2.std(), 2)))


def prune_first_rows(df, n=5):
    return df.iloc[n:]


def convert_index_to_int(df):
    idx = df.index.astype(np.int64)
    new_idx = []
    offset = None
    for i in idx:
        if offset is None:
            offset = i
            new_idx.append(0)
        else:
            new_idx.append(i - offset)
    return df.set_index([new_idx])

