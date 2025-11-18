import os

from dataclasses import dataclass


@dataclass
class Paths:
    root: str  # path to root directory

    @property
    def configs(self, filename: str = 'configs.ini'):
        """Path to directory."""
        return os.path.join(self.root, filename)
