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

query.get_all_day_ahead_data()

