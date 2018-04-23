import matplotlib.pyplot as plt
import numpy as np
import time
import keys
import datetime
import math


hr_styles = ['r--', 'r-.', 'r:', 'r-']
oxygen_styles = ['k--', 'k-.', 'k:', 'k-']


def graph_dfs(data_frames):
    """Graphs a list of data frames"""
    ax = data_frames[0].plot()
    for df in data_frames[1:]:
        df.plot(ax=ax, kind="line")
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
        df1, df2 = get_intersection(d1.df, d2.df)
        method = 'pearson'
        o2_corr = df1[keys.O2].corr(df2[keys.O2], method=method)
        hr_corr = df1[keys.HR].corr(df2[keys.HR], method=method)
        print("\nAnalyzing Device Correlations: ")
        print("(" + str(d1) + ") <=> (" + str(d2) + ")")
        print("O2 Correlation (" + method + ") = " + str(o2_corr))
        print("HR Correlation (" + method + ") = " + str(hr_corr))


def print_errors(trial):
    sample_range = datetime.timedelta(milliseconds=20)
    hr_errors = []
    o2_errors = []
    n = 0.0
    for d1, d2 in trial.device_combinations():
        print("\nAnalyzing Device Errors: ")
        print("(" + str(d1) + ") <=> (" + str(d2) + ")")
        df_start, df_end = get_common_endpoints(d1.df, d2.df)
        sample_date = df_start
        while sample_date < df_end:
            data1 = d1.df.iloc[d1.df.index.get_loc(sample_date, method='nearest')]
            data2 = d2.df.iloc[d2.df.index.get_loc(sample_date, method='nearest')]
            hr_1, hr_2 = data1[keys.HR], data2[keys.HR]
            o2_1, o2_2 = data1[keys.O2], data2[keys.O2]
            hr_errors.append(hr_1 - hr_2)
            o2_errors.append(o2_1 - o2_2)
            n += 1
            sample_date += sample_range
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


def get_intersection(df1, df2):
    """Returns the two data frames, trimmed to the common overlap between them"""
    df_start, df_end = get_common_endpoints(df1, df2)
    df1_intersect = df1.loc[df_start: df_end]
    df2_intersect = df2.loc[df_start: df_end]
    return df1_intersect, df2_intersect


def get_common_endpoints(df1, df2):
    df_start = df1.index[0] if (df1.index[0] > df2.index[0]) else df2.index[0]
    df_end = df1.index[-1] if (df1.index[-1] < df2.index[-1]) else df2.index[-1]
    return df_start, df_end


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

