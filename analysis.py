import matplotlib.pyplot as plt
import numpy as np
import time

def graph_dfs(data_frames):
    """Graphs a list of data frames"""
    ax = data_frames[0].plot()
    for df in data_frames[1:]:
        df.plot(ax=ax, kind="line")
    plt.show()


def graph_devices(devices):
    legend = []
    ax = None
    for device in devices:
        df = prune_first_rows(device.df)
        if ax is None:
            ax = df.plot()
        else:
            df.plot(ax=ax)
        legend.append(device.user_description + " HR")
        legend.append(device.user_description + " Oxygen")
    ax.legend(legend)
    ax.set_xlabel("Time")
    ax.set_ylabel("Heart-Rate (BPM)   Oxygen Saturation (%)")
    plt.savefig('./report/images/raw/trial-' + str(devices[0].trial.description) + '-plot-' + str(time.time()) + '.png')
    plt.show()


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

