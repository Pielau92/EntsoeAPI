import pandas as pd

def create_empty_hourly_df(start:pd.Timestamp, end:pd.Timestamp):
    """Create empty DataFrame with hourly DatetimeIndex.

    :param pd.Timestamp start:  start time
    :param pd.Timestamp end: end time (included)
    :return: empty DataFrame with hourly DatetimeIndex.
    """

    # index with hourly timestamps
    index = pd.date_range(start=start, end=end, freq='h')

    return pd.DataFrame(index=index)

