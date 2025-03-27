import os, sys

import pandas as pd


def get_root_dir() -> str:
    """Get root directory path."""

    if getattr(sys, 'frozen', False):  # if program is run from an executable .exe file
        return os.path.dirname(os.path.dirname(sys.executable))
    else:  # if program is run from IDE or command window
        return os.path.dirname(os.path.dirname(__file__))


def create_empty_hourly_df(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Create empty DataFrame with hourly DatetimeIndex.

    :param pd.Timestamp start:  start time
    :param pd.Timestamp end: end time (included)
    :return: empty DataFrame with hourly DatetimeIndex.
    """

    # index with hourly timestamps
    index = pd.date_range(start=start, end=end, freq='h')[:-1]  # drop entry for midnight

    return pd.DataFrame(index=index)
