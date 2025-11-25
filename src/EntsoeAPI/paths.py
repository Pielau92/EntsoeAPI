import os

from dataclasses import dataclass


@dataclass
class Paths:
    root: str  # path to root directory

    @property
    def configs(self, filename: str = 'configs.ini') -> str:
        """Path to directory."""
        return os.path.join(self.root, filename)

    @property
    def output_dir(self) -> str:
        """Path to output directory."""
        return os.path.join(self.root, 'data')
