# TODO: a DS will implement real robustness metric for sales time series
# You may implement it if you want
# cluster_time_series is date | sales (daily sales)


def is_cluster_robust(cluster_time_series):
    # for now 500 sales is enough
    return cluster_time_series['sales'].sum() >= 500
