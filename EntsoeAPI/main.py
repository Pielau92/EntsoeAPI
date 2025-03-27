import datetime, sys, os

import pandas as pd

from classes import DataQuery


def get_root_dir() -> str:
    """Get root directory path."""

    if getattr(sys, 'frozen', False):  # if program is run from an executable .exe file
        return os.path.dirname(os.path.dirname(sys.executable))
    else:  # if program is run from IDE or command window
        return os.path.dirname(os.path.dirname(__file__))


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

# Export as csv files
forecast_yesterday.to_csv('../data/forecast_yesterday.csv')
forecast_today.to_csv('../data/forecast_today.csv')
historical_yesterday.to_csv('../data/historical_yesterday.csv')

if forecast_tomorrow:
    forecast_tomorrow.to_csv('../data/forecast_tomorrow.csv')

pass
