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


class PathConfig:
    """Class for storing path information."""

    def __init__(self, data_query: any, root_dir: str):
        self.data_query = data_query
        self.root = root_dir

    @property
    def configs(self, filename: str = 'configs.ini'):
        """Path to directory."""
        return os.path.join(self.root, filename)
