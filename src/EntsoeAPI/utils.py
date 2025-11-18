import os, sys

import pandas as pd

from configparser import ConfigParser


def get_pardir(path: str, levels: int = 1) -> str:
    """Get parent directory of given path.

    It is possible to go up multiple levels using the levels parameter.

    :param str path: initial path
    :param int levels: determines how many levels upwards the function goes
    :return: parent directory, single (default) or multiple levels upwards
    """

    pardir = path
    for _ in range(levels):
        pardir = os.path.dirname(pardir)

    return pardir


def get_root_dir() -> str:
    """Get root directory path."""

    # if program is run from...
    if getattr(sys, 'frozen', False):  # an executable .exe file
        filepath = sys.executable
    else:  # IDE or command window
        filepath = __file__

    return get_pardir(path=filepath, levels=3)


def create_empty_hourly_df(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Create empty DataFrame with hourly DatetimeIndex.

    :param pd.Timestamp start: start time
    :param pd.Timestamp end: end time (included)
    :return: empty DataFrame with hourly DatetimeIndex
    """

    # index with hourly timestamps
    index = pd.date_range(start=start, end=end, freq='h')[:-1]  # drop entry for midnight

    return pd.DataFrame(index=index)


def get_empty_df(start: pd.Timestamp, end: pd.Timestamp, freq: str = 'h', columns: list[str] = [],
                 data=float('nan')) -> pd.DataFrame:
    """Create DataFrame with datetime indices and

    :param pd.Timestamp start: start of datetime indices
    :param pd.Timestamp end: end of datetime indices
    :param str freq: time increment of datetime indices
    :param list[str] columns: column headers
    :param data: default data value
    :return: empty DataFrame
    """

    # create datatime indices in
    kwargs = {'index': pd.date_range(start=start, end=end, freq=freq)}

    if columns:
        kwargs.update({
            'columns': columns,
            'data': data
        })

    return pd.DataFrame(**kwargs)
