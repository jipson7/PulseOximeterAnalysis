import matplotlib.pyplot as plt


def graph_dfs(data_frames):
    """Graphs a list of data frames"""
    ax = data_frames[0].plot()
    for df in data_frames[1:]:
        df.plot(ax=ax, kind="line")
    plt.show()


def get_intersection(df1, df2):
    """Returns the two data frames, trimmed to the common overlap between them"""
    df_start = df1.index[0] if (df1.index[0] > df2.index[0]) else df2.index[0]
    df_end = df1.index[-1] if (df1.index[-1] < df2.index[-1]) else df2.index[-1]
    df1_intersect = df1.loc[df_start: df_end]
    df2_intersect = df2.loc[df_start: df_end]
    return df1_intersect, df2_intersect
