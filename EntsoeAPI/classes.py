import os

import pandas as pd

from configparser import ConfigParser
from entsoe import EntsoePandasClient
from entsoe.mappings import lookup_area, NEIGHBOURS
from EntsoeAPI.utils import create_empty_hourly_df


class DataQuery:
    """Class for storing data query configurations."""

    def __init__(self, root_dir: str):
        self.api_key = str()  # API security token from ENTSO E
        self.country_code = str()  # unique code of target country - see entsoe.mappings.Area class for complete table
        self.day_ahead_deadline = str()  # deadline for publication of day ahead data

        # paths
        self.path = PathConfig(self, root_dir)
        self.settings = Settings(self)
        self.settings.load_settings()
        self.settings.apply_settings()

        self.tz = lookup_area(self.country_code).tz  # time zone
        self.date_today = None  # today's date

        self.client = EntsoePandasClient(api_key=self.api_key)  # ENTSO E client
        self.set_date_today()

    def set_date_today(self) -> None:
        """Set today's date."""

        date_today = pd.to_datetime('today').normalize()  # datetime: today at midnight
        date_today = pd.Timestamp(date_today, tz=self.tz)  # add timezone information
        self.date_today = date_today  # set value

    def get_all_day_ahead_data(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """Get all day ahead data for a specified time period.

        The time period can be in the past or future, depending on the dataset.

        :param start: start datetime of requested time period
        :param end: end datetime of requested time period
        :return: DataFrame with requested data
        """

        data = dict()

        # energy prices [€/MWh]
        data['energy_prices'] = self.client.query_day_ahead_prices(
            country_code=self.country_code,
            start=start,
            end=end,
        )

        # wind onshore and solar generation forecast [MW]
        df_response = self.client.query_wind_and_solar_forecast(
            self.country_code,
            start=start,
            end=end,
            psr_type=None,
        )
        data['solar_generation'] = df_response['Solar']
        data['wind_onshore_generation'] = df_response['Wind Onshore']

        # total load forecast[MW]
        df_response = self.client.query_load_and_forecast(
            self.country_code,
            start=start,
            end=end,
        )
        data['total_load'] = df_response['Actual Load']

        # cross-border physical flow forecast (scheduled commercial exchange with neighbors) [MW]
        for neighbour in NEIGHBOURS[self.country_code]:
            data[f'scheduled_exchange_{neighbour}'] = self.client.query_scheduled_exchanges(
                country_code_from=self.country_code,
                country_code_to=neighbour,
                start=start,
                end=end,
                dayahead=False,
            )

        # save collected data as DataFrame
        # assumes datetimes from df automatically (if data has >1 value per hour, only the first value is saved)
        df = create_empty_hourly_df(start, end)
        for key in data:
            df[key] = data[key]

        return df

    def get_all_historical_data(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """Get all historic data for a specified time period.

        :param start: start datetime of requested time period
        :param end: end datetime of requested time period
        :return: DataFrame with requested data
        """

        data = dict()

        # total load [MW]
        df_response = self.client.query_load(self.country_code, start=start, end=end)
        data['total_load'] = df_response['Actual Load']

        # wind onshore and solar generation [MW]
        df_response = self.client.query_generation(self.country_code, start=start, end=end, psr_type=None)
        data['solar_generation'] = df_response[('Solar', 'Actual Aggregated')]
        data['wind_onshore_generation'] = df_response[('Wind Onshore', 'Actual Aggregated')]

        # cross-border physical flow (scheduled commercial exchange with neighbors) [MW]
        for neighbour in NEIGHBOURS[self.country_code]:
            data[f'scheduled_exchange_{neighbour}'] = self.client.query_crossborder_flows(
                country_code_from=self.country_code,
                country_code_to=neighbour,
                end=end,
                start=start,
                lookup_bzones=True)

        # save data as DataFrame
        df = create_empty_hourly_df(start, end)
        for key in data:
            df[key] = data[key]

        return df


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
