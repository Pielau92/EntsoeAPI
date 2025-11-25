import pandas as pd

from entsoe import EntsoePandasClient
from entsoe.mappings import lookup_area

from EntsoeAPI.utils import get_date_today
from EntsoeAPI.paths import Paths
from EntsoeAPI.configs import Configs


class Session:
    """Class for storing data query configurations."""

    def __init__(self, root_dir: str):
        self.path = Paths(root_dir)
        self.configs = Configs(self.path.configs)

        self.client = EntsoePandasClient(api_key=self.configs.general.api_key)  # ENTSO E client

        self.tz: str = lookup_area(self.configs.general.country_code).tz  # time zone
        self.date_today: pd.Timestamp = get_date_today(self.tz)  # today's date


if __name__ == '__main__':
    from EntsoeAPI.utils import get_root_dir

    session = Session(root_dir=get_root_dir())
    pass
