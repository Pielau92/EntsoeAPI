import datetime, sys, os

from entsoe import EntsoePandasClient
from entsoe.mappings import lookup_area, NEIGHBOURS
import pandas as pd

from classes import DataQuery


def get_root_dir():
    """Get root directory path."""

    if getattr(sys, 'frozen', False):  # if program is run from an executable .exe file
        return os.path.dirname(os.path.dirname(sys.executable))
    else:  # if program is run from IDE or command window
        return os.path.dirname(os.path.dirname(__file__))


query = DataQuery(get_root_dir())

# yesterday
start = query.date_today - pd.DateOffset(days=1)
end = query.date_today
yesterday = query.get_all_day_ahead_data(start, end)

# today
start += pd.DateOffset(days=1)
end += pd.DateOffset(days=1)
today = query.get_all_day_ahead_data(start, end)

# tomorrow
if datetime.datetime.now().time() < datetime.datetime.strptime(query.day_ahead_deadline, '%H:%M').time():
    print(f'Day ahead prognosis data not available until today {query.day_ahead_deadline}')
else:
    start += pd.DateOffset(days=1)
    end += pd.DateOffset(days=1)
    tomorrow = query.get_all_day_ahead_data(start, end)

# historical yesterday
start = query.date_today - pd.DateOffset(days=1)
end = query.date_today
historical_yesterday = query.get_all_historical_data(start, end)


# WRITE pandas
# r.to_csv('outfile.csv')

