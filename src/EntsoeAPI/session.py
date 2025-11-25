import configparser

from dataclasses import fields

from entsoe import EntsoePandasClient
from entsoe.mappings import lookup_area

from EntsoeAPI.utils import get_date_today, parse_optional_list
from EntsoeAPI.paths import Paths
from EntsoeAPI.configs import Configs, Runtime
from EntsoeAPI.dataset import Dataset


class Session:
    """Class for storing data query configurations."""

    def __init__(self, root_dir: str):
        self.path = Paths(root_dir)
        self.configs = Configs(self.path.configs)

        self.client = EntsoePandasClient(api_key=self.configs.general.api_key)  # ENTSO E client

        self.datasets: list[Dataset] | None = None

        # set runtime configurations
        timezone = lookup_area(self.configs.general.country_code).tz
        self.configs.runtime = Runtime(
            tz=timezone,
            date_today=get_date_today(timezone)  # today's date including time zone information
        )

    def load_dataset_configs(self) -> None:
        """Load dataset configurations from .ini file and create a Dataset object for each dataset."""

        # initialize config parser
        config = configparser.ConfigParser()
        config.read(self.path.configs)

        datasets = []
        for section in config.sections():

            sections = [field.type._section_name for field in fields(Configs) if hasattr(field.type, '_section_name')]
            if section in sections:
                continue  # ignore any fixed ini section

            params = {field:  # key
                          parse_optional_list(config.get(section, field))  # value
                      for field in
                      ['queries', 'timeperiods', 'export_formats']}  # name of dataset fields inside .ini file

            params['name'] = section
            params['client'] = self.client
            params['configs'] = self.configs

            datasets.append(Dataset(**params))

        self.datasets = datasets


if __name__ == '__main__':
    from EntsoeAPI.utils import get_root_dir

    session = Session(root_dir=get_root_dir())
    session.load_dataset_configs()
    pass
