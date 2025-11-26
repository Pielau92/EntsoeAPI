import pandas as pd

from typing import Callable

from entsoe import EntsoePandasClient
from entsoe.mappings import NEIGHBOURS, PSRTYPE_MAPPINGS
from entsoe.exceptions import NoMatchingDataError

from EntsoeAPI.utils import create_empty_hourly_df, get_empty_df
from EntsoeAPI.configs import Configs
from EntsoeAPI.timeperiod import TimePeriod

type Query = Callable[[EntsoePandasClient, Configs, pd.Timestamp, pd.Timestamp], pd.DataFrame]
"""
:param EntsoePandasClient client: client from entsoe package
:param Configs configs: configurations
:param pd.Timestamp start: start datetime of requested time period
:param pd.Timestamp end: end datetime of requested time period
:return: DataFrame with requested data
"""


def day_ahead_prices(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp,
                     end: pd.Timestamp) -> pd.DataFrame:
    return client.query_day_ahead_prices(country_code=configs.general.country_code, start=start, end=end)


def wind_and_solar_generation(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp,
                              end: pd.Timestamp) -> pd.DataFrame:
    return client.query_wind_and_solar_forecast(
        configs.general.country_code, start=start, end=end, psr_type=None)


def load_forecast(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return client.query_load_forecast(configs.general.country_code, start=start, end=end)

def load(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return client.query_load(configs.general.country_code, start=start, end=end)

def scheduled_exchanges(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    data = {
        neighbour:  # key
            client.query_scheduled_exchanges(  # response as value
                country_code_from=configs.general.country_code,
                country_code_to=neighbour,
                start=start,
                end=end,
                dayahead=False, )
        for neighbour in NEIGHBOURS[configs.general.country_code]  # for each neighbour country
    }

    return pd.DataFrame(data)


def get_all_day_ahead_data(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp,
                           end: pd.Timestamp) -> pd.DataFrame:
    """Get all day ahead data for a specified time period."""

    # combine multiple base queries
    query_list = ['day_ahead_prices', 'wind_and_solar_generation', 'load', 'scheduled_exchanges']

    responses = {query_name: get_query(client, configs, start, end, query_name) for query_name in query_list}

    # save collected data as DataFrame
    # assumes datetimes from df automatically (if data has >1 value per hour, only the first value is saved)
    df = create_empty_hourly_df(start, end)

    df['energy_prices [EUR/MWh]'] = responses['day_ahead_prices']
    df['solar_generation [MW]'] = responses['wind_and_solar_generation']['Solar']
    df['wind_onshore_generation [MW]'] = responses['wind_and_solar_generation']['Wind Onshore']
    df['total_load [MW]'] = responses['load']
    for neighbour in NEIGHBOURS[configs.general.country_code]:
        df[f'scheduled_exchange_{neighbour} [MW]'] = responses['scheduled_exchanges'][neighbour]

    return df


def get_all_historical_data(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp,
                            end: pd.Timestamp) -> pd.DataFrame:
    """Get all historic data for a specified time period."""

    data = dict()

    # total load [MW]
    df_response = client.query_load(configs.general.country_code, start=start, end=end)
    data['total_load [MW]'] = df_response['Actual Load']

    # wind onshore and solar generation [MW]
    df_response = client.query_generation(configs.general.country_code, start=start, end=end,
                                          psr_type=None)
    data['solar_generation [MW]'] = df_response[('Solar', 'Actual Aggregated')]
    data['wind_onshore_generation [MW]'] = df_response[('Wind Onshore', 'Actual Aggregated')]

    # cross-border physical flow (scheduled commercial exchange with neighbors) [MW]
    for neighbour in NEIGHBOURS[configs.general.country_code]:
        data[f'scheduled_exchange_{neighbour} [MW]'] = client.query_crossborder_flows(
            country_code_from=configs.general.country_code,
            country_code_to=neighbour,
            end=end,
            start=start,
            lookup_bzones=True)

    # day ahead price data [€/MWh]
    df_response = client.query_day_ahead_prices(configs.general.country_code, start=start, end=end,
                                                resolution='15min')
    data['day_ahead [€/MWh]'] = df_response

    # save data as DataFrame
    df = create_empty_hourly_df(start, end)
    for key in data:
        df[key] = data[key]

    return df


def get_generation_data_by_energy_source(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp,
                                         end: pd.Timestamp) -> pd.DataFrame:
    """Get energy generation data for each energy source."""

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
                response = client.query_generation(
                    country_code=configs.general.country_code, start=start, end=end, psr_type=psr_type)
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


def get_energy_imports(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp,
                       end: pd.Timestamp) -> pd.DataFrame:
    empty_df = get_empty_df(start=start, end=end, columns=NEIGHBOURS[configs.general.country_code])

    empty_df.update(client.query_import(
        country_code=configs.general.country_code,
        start=start,
        end=end
    ).resample('h').first())

    return empty_df


# simple queries
queries: dict[str, Query] = {
    'day_ahead_prices': day_ahead_prices,
    'wind_and_solar_generation': wind_and_solar_generation,
    'load': load,
    'scheduled_exchanges': scheduled_exchanges,
}

# complex queries (consisting of multiple simple queries)
queries.update({
    "forecast": get_all_day_ahead_data,
    "historical": get_all_historical_data,
    "generation_by_source": get_generation_data_by_energy_source,
    "imports": get_energy_imports,
})


def get_query(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp, query_name: str) \
        -> pd.DataFrame | None:
    query = queries[query_name]
    try:
        return query(client, configs, start, end)
    except NoMatchingDataError:
        print(f'NoMatchingDataError encountered, skipping request...')
