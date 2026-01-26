import os
import openpyxl

import pandas as pd

from typing import Callable

type ExportFn = Callable[[pd.DataFrame, str], None]


def export_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path)


def export_xlsx(data: pd.DataFrame, path: str) -> None:
    df_tz_naive = data.copy().tz_localize(None)  # turn into timezone naive dataset
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df_tz_naive.to_excel(writer)


def export_xlsx_multisheet(data: dict[str, pd.DataFrame], path: str) -> None:
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        for key, df in data.items():
            df_tz_naive = df.copy().tz_localize(None)  # turn into timezone naive dataset
            df_tz_naive.to_excel(writer, sheet_name=str(key))


def export_csv_stacked(data: dict[str, pd.DataFrame], path: str) -> None:
    # remove last row to avoid duplicates (last value in data is identical to first value in data of adjacent timeperiod)
    data = {key: data[key].iloc[:-1] for key in data.keys()}

    df = pd.concat(data.values())  # stack data
    df = df.sort_index()  # sort chronologically
    df.to_csv(path)  # export


exporters: dict[str, ExportFn] = {
    'csv': export_csv,
    'xlsx': export_xlsx,
    'xlsx_multisheet': export_xlsx_multisheet,
    'csv_stacked': export_csv_stacked,
}


def export_data(data: pd.DataFrame, path: str, format: str) -> None:
    print(f'Exporting to {path}')
    exporter = exporters[format]
    exporter(data, path)


def export_batch(datasets: dict[str, pd.DataFrame], dirpath: str, format: str) -> None:
    for key, data in datasets.items():
        if data is not None:
            export_path = os.path.join(dirpath, f'{key}.{format}')
            export_data(data=data, path=export_path, format=format)
        else:
            print(f'No data for {key}')
