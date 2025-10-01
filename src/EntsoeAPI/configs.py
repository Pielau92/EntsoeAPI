from dataclasses import dataclass

from simple_config_manager.configs import _Configs


@dataclass
class General:
    """Explanatory comment about section (optional)"""
    # mandatory field if to be filled with values from .ini file, must match with section name used inside .ini file!
    _section_name = 'General'

    api_key: str  # API security token from ENTSO E
    country_code: str  # unique code of target country - see entsoe.mappings.Area class for complete table
    day_ahead_deadline: str  # deadline for publication of day ahead data


@dataclass(init=False)
class Configs(_Configs):

    general: General
    
