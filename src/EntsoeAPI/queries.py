import pandas as pd

from typing import Callable

from entsoe import EntsoePandasClient
from entsoe.mappings import NEIGHBOURS
from entsoe.exceptions import NoMatchingDataError

from EntsoeAPI.utils import create_empty_hourly_df
from EntsoeAPI.configs import Configs

type Query = Callable[[EntsoePandasClient, Configs, pd.Timestamp, pd.Timestamp], pd.DataFrame]
"""
:param EntsoePandasClient client: client from entsoe package
:param Configs configs: configurations
:param pd.Timestamp start: start datetime of requested time period
:param pd.Timestamp end: end datetime of requested time period
:return: DataFrame with requested data
"""

tab_lvl: int = 0


def day_ahead_prices(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    response = (client.query_day_ahead_prices(
        country_code=configs.general.country_code, start=start, end=end, resolution='15min'))
    response = pd.DataFrame(response)  # convert to DataFrame
    response.columns = ['energy_prices [EUR/MWh]']  # overwrite column header
    return response


def wind_and_solar_generation_forecast(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    response: pd.DataFrame = client.query_wind_and_solar_forecast(
        configs.general.country_code, start=start, end=end, psr_type=None)
    mapping = {
        'Solar': 'solar_generation [MW]',
        'Wind Onshore': 'wind_onshore_generation [MW]',
    }
    response.columns = [mapping.get(col_name, col_name) for col_name in response.columns]  # overwrite column headers
    return response


def generation(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    response = client.query_generation(configs.general.country_code, start=start, end=end)
    response = response[[col for col in response.columns if col[1] == 'Actual Aggregated']]  # get generation data only
    response.columns = [f'generation_{col[0]} [MW]' for col in response.columns]  # overwrite column names
    return response


def load_forecast(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    response = client.query_load_forecast(configs.general.country_code, start=start, end=end)
    response.columns = ['load_forecast [MW]']
    return response


def load(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    response = client.query_load(configs.general.country_code, start=start, end=end)
    response.columns = ['total_load [MW]']  # overwrite column names
    return response


def scheduled_exchanges(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    data = {}
    for neighbour in NEIGHBOURS[configs.general.country_code]:
        try:
            data[f'scheduled_exchange_{neighbour} [MW]'] = client.query_scheduled_exchanges(
                country_code_from=configs.general.country_code,
                country_code_to=neighbour,
                start=start,
                end=end,
                dayahead=False,
            )
        except ValueError:
            print(f'{'\t' * tab_lvl}No scheduled exchange data found for {neighbour}.')

    return pd.DataFrame(data)


def crossborder_exchange(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    responses = {}
    for neighbour in NEIGHBOURS[configs.general.country_code]:
        try:
            responses[f'scheduled_exchange_{neighbour} [MW]'] = client.query_crossborder_flows(
                country_code_from=configs.general.country_code,
                country_code_to=neighbour,
                end=end,
                start=start,
                lookup_bzones=True,
            )
        except ValueError:
            print(f'{'\t' * tab_lvl}No crossborder exchange data found for {neighbour}.')

    return pd.DataFrame(responses)


def imports(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame | None:
    try:
        response = client.query_import(
            country_code=configs.general.country_code,
            start=start,
            end=end,
        )

    except ValueError:
        print(f'{'\t' * tab_lvl}No imports data found.')
        return

    # overwrite column headers
    response.columns = [f'energy_imports_{col_name} [MW]' for col_name in response.columns]

    return response


def get_all_forecast_data(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Get all day ahead data for a specified time period."""

    # combine multiple base queries
    query_list = [
        'day_ahead_prices',
        'wind_and_solar_generation_forecast',
        'load',
        'scheduled_exchanges'
    ]

    responses = {query_name: get_query(client, configs, start, end, query_name) for query_name in query_list}

    # save collected data as DataFrame
    # assumes datetimes from df automatically (if data has >1 value per hour, only the first value is saved)
    df = create_empty_hourly_df(start, end)

    for query_name in query_list:
        for col_name in list(responses[query_name].columns):
            df[col_name] = responses[query_name][col_name]

    return df


def get_all_historical_data(
        client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Get all historic data for a specified time period."""

    # combine multiple base queries
    query_list = [
        'load',
        'generation',
        'crossborder_exchange',
        'day_ahead_prices'
    ]

    responses = {query_name: get_query(client, configs, start, end, query_name) for query_name in query_list}

    # save data as DataFrame
    # assumes datetimes from df automatically (if data has >1 value per hour, only the first value is saved)
    df = create_empty_hourly_df(start, end)

    df['total_load [MW]'] = responses['load']
    df = pd.concat([df, responses['generation']], axis=1)
    df['day_ahead [€/MWh]'] = responses['day_ahead_prices']

    return df


# basic queries
queries: dict[str, Query] = {
    'day_ahead_prices': day_ahead_prices,
    'wind_and_solar_generation_forecast': wind_and_solar_generation_forecast,
    'generation': generation,
    'load_forecast': load_forecast,
    'load': load,
    'scheduled_exchanges': scheduled_exchanges,
    'crossborder_exchange': crossborder_exchange,
    'imports': imports,
}

# complex queries (consisting of multiple simple queries)
queries.update({
    "forecast": get_all_forecast_data,
    "historical": get_all_historical_data,
})


def get_query(client: EntsoePandasClient, configs: Configs, start: pd.Timestamp, end: pd.Timestamp, query_name: str) \
        -> pd.DataFrame | None:
    query = queries[query_name]
    global tab_lvl
    print(f'{'\t' * tab_lvl}Requesting {query_name} data from {start.strftime('%Y-%m-%d %X')} to '
          f'{end.strftime('%Y-%m-%d %X')}...')
    try:
        tab_lvl += 1
        response = query(client, configs, start, end)
        print(f'{'\t' * tab_lvl}Successfull')
        tab_lvl -= 1
        return response
    except NoMatchingDataError:
        print(f'{'\t' * tab_lvl}NoMatchingDataError encountered, skipping request...')
    # except Exception as error:
    #     print(f'{'\t' * tab_lvl}Unspecified error {repr(error)} occured')

    tab_lvl -= 1
