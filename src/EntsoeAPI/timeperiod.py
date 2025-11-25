import pandas as pd


class TimePeriod:
    """Provide start and end timestamps for a day relative to a given date, or for a given year. Timezone information is
    conserved."""

    def __init__(self, date: pd.Timestamp):
        self.date = date

    @property
    def yesterday(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        start = self.date - pd.DateOffset(days=1)
        end = self.date
        return start, end

    @property
    def today(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        start = self.date
        end = self.date + pd.DateOffset(days=1)
        return start, end

    @property
    def tomorrow(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        start = self.date + pd.DateOffset(days=1)
        end = self.date + pd.DateOffset(days=2)
        return start, end

    def year(self, year: int) -> tuple[pd.Timestamp, pd.Timestamp]:
        start = pd.Timestamp(year=year, month=1, day=1, hour=0, minute=0, second=0, tz=self.date.tz)
        end = start + pd.DateOffset(years=1)
        return start, end
