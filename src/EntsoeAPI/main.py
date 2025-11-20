import os
import datetime

from EntsoeAPI.dataquery import DataQuery
from EntsoeAPI.timeperiod import TimePeriod
from EntsoeAPI.utils import get_root_dir
from EntsoeAPI.queries import get_query
from EntsoeAPI.exporters import export_batch

root = get_root_dir()

query = DataQuery(root)

today = query.date_today  # today's date

timeperiod = TimePeriod(today)

# region ASSEMBLE PARAMETERS

params: list[tuple[str, str | int]] = []

# add forecast data requests
params.append(('forecast', 'yesterday'))
params.append(('forecast', 'today'))

# add forecast data request for tomorrow, if available
if datetime.datetime.now().time() < datetime.datetime.strptime(query.configs.general.day_ahead_deadline,
                                                               '%H:%M').time():
    print(f'Day ahead prognosis data not available until today {query.configs.general.day_ahead_deadline}.')
else:
    params.append(('forecast', 'tomorrow'))

# add yearly historical data requests
[params.append(('historical', year)) for year in query.configs.general.years]

# add yearly generation by energy source data requests
[params.append(('generation_by_source', year)) for year in query.configs.general.years]

# add yearly generation by energy source data requests
[params.append(('imports', year)) for year in query.configs.general.years]

# endregion

# perform API requests
datasets = {f'{query_name}_{tp}': get_query(data_query=query, tp=tp, query_name=query_name) for query_name, tp in
            params}

# perform export to csv
export_batch(datasets=datasets, dirpath=os.path.join(root, 'data'), format='csv')

print('done!')
