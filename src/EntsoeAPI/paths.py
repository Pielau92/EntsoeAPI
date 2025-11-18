import os

from EntsoeAPI.dataquery import DataQuery

class PathConfig:
    """Class for storing path information."""

    def __init__(self, data_query: DataQuery, root_dir: str):
        self.data_query = data_query
        self.root = root_dir

    @property
    def configs(self, filename: str = 'configs.ini'):
        """Path to directory."""
        return os.path.join(self.root, filename)
