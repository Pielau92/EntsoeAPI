import datetime, os

import pandas as pd

from configparser import ConfigParser
from entsoe import EntsoePandasClient
from entsoe.mappings import lookup_area, NEIGHBOURS


class DataQuery:
    """Class for storing configurations"""

    def __init__(self, root_dir):
        self.api_key = str()
        self.country_code = str()
        self.day_ahead_deadline = str()

        self.path = PathConfig(self, root_dir)
        self.settings = Settings(self)
        self.settings.load_settings()
        self.settings.apply_settings()

        self.tz = lookup_area(self.country_code).tz
        self.date_today = None

        self.client = EntsoePandasClient(api_key=self.api_key)
        self.set_date_today()

    def set_date_today(self):
        date_today = pd.to_datetime('today').normalize()  # datetime: today at midnight
        date_today = pd.Timestamp(date_today, tz=self.tz)  # add timezone information
        self.date_today = date_today


class PathConfig:

    def __init__(self, data_query, root_dir):
        self.data_query = data_query
        self.root = root_dir

    @property
    def settings(self, filename='settings.ini'):
        """Path to directory."""
        return os.path.join(self.root, filename)


class Settings:
    """Class for storing settings of SimulationSeries object."""

    def __init__(self, data_query):
        self.data_query = data_query
        self._save_path = data_query.path.settings
        self._settings = ConfigParser()
        self._settings.optionxform = str  # keeps capital letters when reading .ini file

    def load_settings(self):
        try:
            self._settings.read(self._save_path)
        except:
            print("Format error in settings file, check settings.ini")
            raise SystemExit()

    def apply_settings(self):
        """Apply imported settings to SimulationSeries object.

        Applies the imported settings from the settings Excel file to the corresponding attributes of the
        SimulationSeries object with the same name.
        """

        def apply_setting():
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
