import datetime

import pandas as pd

from classes import DataQuery
from utils import get_root_dir

query = DataQuery(get_root_dir())
today = query.date_today  # today's date

# gather request parameters
params = {
    ('forecast', 'yesterday'): {
        'start': today - pd.DateOffset(days=1),
        'end': today},
    ('forecast', 'today'): {
        'start': today,
        'end': today + pd.DateOffset(days=1)},
    ('historical', 'yesterday'): {
        'start': today - pd.DateOffset(days=1),
        'end': today},
}

# add forecast data request for tomorrow, if available
if datetime.datetime.now().time() < datetime.datetime.strptime(query.day_ahead_deadline, '%H:%M').time():
    print(f'Day ahead prognosis data not available until today {query.day_ahead_deadline}.')
else:
    params[('forecast', 'tomorrow')] = {'start': today, 'end': today + pd.DateOffset(days=1)}

# add historical data requests for past years, since 2022
years = list(range(2022, datetime.date.today().year + 1))
for _year in years:
    start = pd.Timestamp(year=_year, month=1, day=1, hour=0, minute=0, second=0, tz=query.tz)
    end = start + pd.DateOffset(years=1) - pd.Timedelta(hours=1)
    params[('historical', str(_year))] = {'start': start, 'end': end}

# perform API requests and csv export
for _key in params:
    req_type: str = _key[0]  # request type (forecast or historical)
    period: str = _key[1]
    start: pd.Timestamp = params[_key]['start']
    end: pd.Timestamp = params[_key]['end']

    print(f'Requesting data: {req_type}, {period}.')
    if req_type == 'forecast':
        data = query.get_all_day_ahead_data(start, end)
    elif req_type == 'historical':
        data = query.get_all_historical_data(start, end)
    else:
        print(f'Unknown request type "{req_type}"')
        continue

    # export to csv
    export_path = f'../data/{req_type}_{period}.csv'
    print(f'Exporting to {export_path}')
    data.to_csv(export_path)

print('done!')
pass
