import os, sys

import pandas as pd

from configparser import ConfigParser


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


class PathConfig:
    """Class for storing path information."""

    def __init__(self, data_query: any, root_dir: str):
        self.data_query = data_query
        self.root = root_dir

    @property
    def settings(self, filename: str = 'settings.ini'):
        """Path to directory."""
        return os.path.join(self.root, filename)


class Settings:
    """Class for storing settings of SimulationSeries object."""

    def __init__(self, data_query: any):
        self.data_query = data_query
        self._save_path = data_query.path.settings
        self._settings = ConfigParser()
        self._settings.optionxform = str  # keeps capital letters when reading .ini file

    def load_settings(self) -> None:
        try:
            self._settings.read(self._save_path)
        except:
            print("Format error in settings file, check settings.ini")
            raise SystemExit()

    def apply_settings(self) -> None:
        """Apply imported settings to SimulationSeries object.

        Applies the imported settings from the settings Excel file to the corresponding attributes of the
        SimulationSeries object with the same name.
        """

        def apply_setting() -> None:
            """Apply setting value to sim_series.

            Applies the individual settings to the corresponding (name of setting and of class attribute must match).
            Automatically recognizes the type of the setting, based on the type of its corresponding class attribute.
            Raises an error if no corresponding class attribute could be found, or an unsupported type is used (str,
            int, float, bool, list (of strings)).
            """

            if not hasattr(self.data_query, setting):
                raise AttributeError(f'Unknown setting "{setting}" in settings.ini file found.')

            attr = getattr(self.data_query, setting)

            if isinstance(attr, bool):
                value = self._settings.getboolean(section, setting)
            elif isinstance(attr, str):
                value = self._settings.get(section, setting)
            elif isinstance(attr, int):
                value = self._settings.getint(section, setting)
            elif isinstance(attr, float):
                value = self._settings.getfloat(section, setting)
            elif isinstance(attr, list):
                items = self._settings.get(section, setting).split(',')  # apply comma (,) delimiter
                value = [item.strip() for item in items]  # remove whitespaces at beginning/end of strings
            else:
                raise TypeError(f'Unknown type "{type(attr)}" for setting "{setting}" in settings.ini file. '
                                f'Supported types are string, integer, float, boolean and list (of strings).')

            setattr(self.data_query, setting, value)

        for section in self._settings.sections():
            for setting in self._settings.options(section):
                apply_setting()  # save setting value into corresponding class attribute, with the correct datatype
