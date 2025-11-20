import pandas as pd

from entsoe.mappings import NEIGHBOURS, PSRTYPE_MAPPINGS
from entsoe.exceptions import NoMatchingDataError
from EntsoeAPI.utils import create_empty_hourly_df, get_empty_df

import pandas as pd

from typing import Callable
from EntsoeAPI.dataquery import DataQuery

type Query = Callable[[DataQuery, pd.Timestamp, pd.Timestamp], pd.DataFrame]


def get_all_day_ahead_data(dataquery: DataQuery, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Get all day ahead data for a specified time period.

    The time period can be in the past or future, depending on the dataset.
    
    :param dataquery: Dataquery object
    :param start: start datetime of requested time period
    :param end: end datetime of requested time period
    :return: DataFrame with requested data
    """

    data = dict()

    # energy prices [€/MWh]
    data['energy_prices [EUR/MWh]'] = dataquery.client.query_day_ahead_prices(
        country_code=dataquery.configs.general.country_code,
        start=start,
        end=end,
    )

    # wind onshore and solar generation forecast [MW]
    df_response = dataquery.client.query_wind_and_solar_forecast(
        dataquery.configs.general.country_code,
        start=start,
        end=end,
        psr_type=None,
    )
    data['solar_generation [MW]'] = df_response['Solar']
    data['wind_onshore_generation [MW]'] = df_response['Wind Onshore']

    # total load forecast[MW]
    df_response = dataquery.client.query_load_and_forecast(
        dataquery.configs.general.country_code,
        start=start,
        end=end,
    )
    data['total_load [MW]'] = df_response['Forecasted Load']

    # cross-border physical flow forecast (scheduled commercial exchange with neighbors) [MW]
    for neighbour in NEIGHBOURS[dataquery.configs.general.country_code]:
        data[f'scheduled_exchange_{neighbour} [MW]'] = dataquery.client.query_scheduled_exchanges(
            country_code_from=dataquery.configs.general.country_code,
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


def get_all_historical_data(dataquery: DataQuery, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Get all historic data for a specified time period.

    :param dataquery: Dataquery object
    :param start: start datetime of requested time period
    :param end: end datetime of requested time period
    :return: DataFrame with requested data
    """

    data = dict()

    # total load [MW]
    df_response = dataquery.client.query_load(dataquery.configs.general.country_code, start=start, end=end)
    data['total_load [MW]'] = df_response['Actual Load']

    # wind onshore and solar generation [MW]
    df_response = dataquery.client.query_generation(dataquery.configs.general.country_code, start=start, end=end,
                                                    psr_type=None)
    data['solar_generation [MW]'] = df_response[('Solar', 'Actual Aggregated')]
    data['wind_onshore_generation [MW]'] = df_response[('Wind Onshore', 'Actual Aggregated')]

    # cross-border physical flow (scheduled commercial exchange with neighbors) [MW]
    for neighbour in NEIGHBOURS[dataquery.configs.general.country_code]:
        data[f'scheduled_exchange_{neighbour} [MW]'] = dataquery.client.query_crossborder_flows(
            country_code_from=dataquery.configs.general.country_code,
            country_code_to=neighbour,
            end=end,
            start=start,
            lookup_bzones=True)

    # day ahead price data [€/MWh]
    df_response = dataquery.client.query_day_ahead_prices(dataquery.configs.general.country_code, start=start, end=end,
                                                          resolution='15min')
    data['day_ahead [€/MWh]'] = df_response

    # save data as DataFrame
    df = create_empty_hourly_df(start, end)
    for key in data:
        df[key] = data[key]

    return df


def get_generation_data_by_energy_source(dataquery: DataQuery, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Get energy generation data for each energy source.
    
    :param dataquery: Dataquery object 
    :param start: start datetime of requested time period
    :param stop: stop datetime of requested time period
    :return: generation data by energy source
    """

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
                response = dataquery.client.query_generation(
                    country_code=dataquery.configs.general.country_code, start=start, end=end, psr_type=psr_type)
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


def get_energy_imports(dataquery: DataQuery, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    empty_df = get_empty_df(start=start, end=end, columns=NEIGHBOURS[dataquery.configs.general.country_code])

    empty_df.update(dataquery.client.query_import(
        country_code=dataquery.configs.general.country_code,
        start=start,
        end=end
    ).resample('h').first())

    return empty_df


queries: dict[str, Query] = {
    "forecast": get_all_day_ahead_data,
    "historical": get_all_historical_data,
    "generation_by_source": get_generation_data_by_energy_source,
    "imports": get_energy_imports,
}


def get_query(data_query: DataQuery, start: pd.Timestamp, end: pd.Timestamp, query_name: str) -> pd.DataFrame:
    query = queries[query_name]
    return query(data_query, start, end)
