import os

import pandas as pd
from entsoe import EntsoePandasClient

from EntsoeAPI.configs import Configs
from EntsoeAPI.utils import create_empty_hourly_df, get_root_dir
from EntsoeAPI.queries import get_query
from EntsoeAPI.exporters import export_data, export_xlsx_multisheet
from EntsoeAPI.timeperiod import TimePeriod


class Dataset:
    def __init__(self, client: EntsoePandasClient, configs: Configs, name: str, queries: list[str],
                 timeperiods: list[str | int], export_formats: list[str]):
        self.client = client
        self.configs = configs
        self.name = name
        self.queries = queries
        self.timeperiods = timeperiods
        self.export_formats = export_formats

        self.data: dict[tuple[str, str | int], pd.DataFrame] | None = None

    def request_data(self):

        self.data = {}
        for timeperiod in self.timeperiods:
            for query in self.queries:
                self.data[(query, timeperiod)] = get_query(client=self.client, configs=self.configs, tp=timeperiod,
                                                           query_name=query)

        # self.data = {
        #     (query, timeperiod):  # key
        #         get_query(data_query=self.session, tp=timeperiod, query_name=query)  # value
        #     for query in self.queries
        #     for timeperiod in self.timeperiods
        # }

    def export(self):

        pages = {}
        for tp in self.timeperiods:
            timeperiod = TimePeriod(self.configs.runtime.date_today)
            if isinstance(tp, str):
                start, end = timeperiod.__getattribute__(tp)
            elif isinstance(tp, int):
                start, end = timeperiod.year(tp)
            df = create_empty_hourly_df(start, end)
            for query in self.queries:
                df = pd.concat([df, self.data[(query, tp)]], axis=1)
            pages[str(tp)] = df

        for export_format in self.export_formats:
            if export_format == 'csv':
                for key in pages:
                    export_data(
                        data=pages[key],
                        path=os.path.join(get_root_dir(), 'data', f'{key}{'.csv'}'),
                        format='csv',
                    )
            elif export_format == 'xlsx':
                timeperiods = [str(timeperiod) for timeperiod in self.timeperiods]
                export_xlsx_multisheet(
                    data=pages,
                    path=os.path.join(get_root_dir(), 'data',
                                      f'{"&".join(self.queries)}_{"&".join(timeperiods)}{'.xlsx'}',
                                      ),
                )


if __name__ == '__main__':
    from EntsoeAPI.session import Session

    session = Session(root_dir=get_root_dir())
    session.load_dataset_configs()

    for dataset in session.datasets:
        dataset.request_data()
        dataset.export()
