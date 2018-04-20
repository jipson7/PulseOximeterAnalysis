import matplotlib.pyplot as plt
import numpy as np
import time, keys

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
    ax2.set_ylabel("Heart-Rate (BPM)", color='r')
    ax2.tick_params('y', colors='r')
    ax2.set_ylim(bottom=0)
    plt.savefig('./report/images/raw/trial-' + str(trial.description) + '-plot-' + str(time.time()) + '.png')
    plt.show()


def print_correlations(trial):
    for d1, d2 in trial.device_combinations():
        method = 'pearson'
        o2_corr = d1.df[keys.O2].corr(d2.df[keys.O2], method=method)
        hr_corr = d1.df[keys.HR].corr(d2.df[keys.HR], method=method)
        print("\nAnalyzing Device Correlations: ")
        print("(" + str(d1) + ") <=> (" + str(d2) + ")")
        print("O2 Correlation (" + method + ") = " + str(o2_corr))
        print("HR Correlation (" + method + ") = " + str(hr_corr))


def print_stats(trial):
    for device in trial.devices:
        hr = device.df[keys.HR]
        o2 = device.df[keys.O2]
        print("\n" + str(device) + " Stats: ")
        print("HR Mean:    " + str(hr.mean()))
        print("HR Std Dev: " + str(hr.std()))
        print("O2 Mean:    " + str(o2.mean()))
        print("O2 Std Dev: " + str(o2.std()))


def get_intersection(df1, df2):
    """Returns the two data frames, trimmed to the common overlap between them"""
    df_start = df1.index[0] if (df1.index[0] > df2.index[0]) else df2.index[0]
    df_end = df1.index[-1] if (df1.index[-1] < df2.index[-1]) else df2.index[-1]
    df1_intersect = df1.loc[df_start: df_end]
    df2_intersect = df2.loc[df_start: df_end]
    return df1_intersect, df2_intersect


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

