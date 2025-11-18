import pandas as pd

from entsoe import EntsoePandasClient
from entsoe.mappings import lookup_area, NEIGHBOURS, PSRTYPE_MAPPINGS
from entsoe.exceptions import NoMatchingDataError
from EntsoeAPI.utils import create_empty_hourly_df, get_empty_df, get_date_today
from EntsoeAPI.paths import Paths
from EntsoeAPI.configs import Configs


class DataQuery:
    """Class for storing data query configurations."""

    def __init__(self, root_dir: str):
        self.path = Paths(root_dir)
        self.configs = Configs(self.path.configs)

        self.client = EntsoePandasClient(api_key=self.configs.general.api_key)  # ENTSO E client

        self.tz: str = lookup_area(self.configs.general.country_code).tz  # time zone
        self.date_today: pd.Timestamp = get_date_today(self.tz)  # today's date

    def get_all_day_ahead_data(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """Get all day ahead data for a specified time period.

        The time period can be in the past or future, depending on the dataset.

        :param start: start datetime of requested time period
        :param end: end datetime of requested time period
        :return: DataFrame with requested data
        """

        data = dict()

        # energy prices [€/MWh]
        data['energy_prices [EUR/MWh]'] = self.client.query_day_ahead_prices(
            country_code=self.configs.general.country_code,
            start=start,
            end=end,
        )

        # wind onshore and solar generation forecast [MW]
        df_response = self.client.query_wind_and_solar_forecast(
            self.configs.general.country_code,
            start=start,
            end=end,
            psr_type=None,
        )
        data['solar_generation [MW]'] = df_response['Solar']
        data['wind_onshore_generation [MW]'] = df_response['Wind Onshore']

        # total load forecast[MW]
        df_response = self.client.query_load_and_forecast(
            self.configs.general.country_code,
            start=start,
            end=end,
        )
        data['total_load [MW]'] = df_response['Forecasted Load']

        # cross-border physical flow forecast (scheduled commercial exchange with neighbors) [MW]
        for neighbour in NEIGHBOURS[self.configs.general.country_code]:
            data[f'scheduled_exchange_{neighbour} [MW]'] = self.client.query_scheduled_exchanges(
                country_code_from=self.configs.general.country_code,
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
        df_response = self.client.query_load(self.configs.general.country_code, start=start, end=end)
        data['total_load [MW]'] = df_response['Actual Load']

        # wind onshore and solar generation [MW]
        df_response = self.client.query_generation(self.configs.general.country_code, start=start, end=end,
                                                   psr_type=None)
        data['solar_generation [MW]'] = df_response[('Solar', 'Actual Aggregated')]
        data['wind_onshore_generation [MW]'] = df_response[('Wind Onshore', 'Actual Aggregated')]

        # cross-border physical flow (scheduled commercial exchange with neighbors) [MW]
        for neighbour in NEIGHBOURS[self.configs.general.country_code]:
            data[f'scheduled_exchange_{neighbour} [MW]'] = self.client.query_crossborder_flows(
                country_code_from=self.configs.general.country_code,
                country_code_to=neighbour,
                end=end,
                start=start,
                lookup_bzones=True)

        # day ahead price data [€/MWh]
        df_response = self.client.query_day_ahead_prices(self.configs.general.country_code, start=start, end=end,
                                                         resolution='15min')
        data['day_ahead [€/MWh]'] = df_response

        # save data as DataFrame
        df = create_empty_hourly_df(start, end)
        for key in data:
            df[key] = data[key]

        return df

    def get_generation_data_by_energy_source(self, year: int) -> pd.DataFrame:
        """Get energy generation data for each energy source for a given year.

        :param year:
        :return: generation data by energy source
        """

        start = pd.Timestamp(year=year, month=1, day=1, hour=0, minute=0, second=0, tz=self.tz)
        end = start + pd.DateOffset(years=1)

        df_generation = get_empty_df(
            start=start,
            end=end,
            columns=[item for _, item in PSRTYPE_MAPPINGS.items()]
        )

        for psr_type, energy_source in PSRTYPE_MAPPINGS.items():
            success = False
            tries = 2
            while not success:
                try:
                    print(f'Requesting generation data for {energy_source}')
                    response = self.client.query_generation(
                        country_code=self.configs.general.country_code, start=start, end=end, psr_type=psr_type)
                    data = pd.DataFrame(response[(energy_source, 'Actual Aggregated')])
                    data.columns = [energy_source]
                    print('Data found')
                    df_generation.update(data)
                    success = True
                except NoMatchingDataError:
                    print('No data available')
                    success = True
                    continue
                except:
                    print(f'Unknown error occurred for generation data for {energy_source}')
                    if tries > 0:
                        print(f'Trying {tries} more time{['', 's'][tries > 1]}')
                        tries -= 1
                        continue
                    else:
                        break

        return df_generation
