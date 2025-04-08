import datetime, sys, os
import time

import pandas as pd

from classes import DataQuery
from utils import get_root_dir

query = DataQuery(get_root_dir())

# forecast, yesterday
start = query.date_today - pd.DateOffset(days=1)
end = query.date_today
forecast_yesterday = query.get_all_day_ahead_data(start, end)

# forecast, today
start += pd.DateOffset(days=1)
end += pd.DateOffset(days=1)
forecast_today = query.get_all_day_ahead_data(start, end)

# forecast, tomorrow
if datetime.datetime.now().time() < datetime.datetime.strptime(query.day_ahead_deadline, '%H:%M').time():
    print(f'Day ahead prognosis data not available until today {query.day_ahead_deadline}.')
    forecast_tomorrow = None
else:
    start += pd.DateOffset(days=1)
    end += pd.DateOffset(days=1)
    forecast_tomorrow = query.get_all_day_ahead_data(start, end)

# historical, yesterday
start = query.date_today - pd.DateOffset(days=1)
end = query.date_today
historical_yesterday = query.get_all_historical_data(start, end)

# historical, past years since 2022
years = list(range(2022, datetime.date.today().year + 1))
historical_years = dict()
for _year in years:
    start = pd.Timestamp(year=_year, month=1, day=1, hour=0, minute=0, second=0, tz=query.tz)
    end = start + pd.DateOffset(years=1) - pd.Timedelta(hours=1)
    historical_years[str(_year)] = query.get_all_historical_data(start, end)

# Export as csv files
forecast_yesterday.to_csv('../data/forecast_yesterday.csv')
forecast_today.to_csv('../data/forecast_today.csv')
historical_yesterday.to_csv('../data/historical_yesterday.csv')
for key in historical_years:
    historical_years[key].to_csv(f'../data/historical_{key}.csv')

if forecast_tomorrow:
    forecast_tomorrow.to_csv('../data/forecast_tomorrow.csv')

pass
