# Data retrieval script for forecast and historical ENTSO-E data
This script automatically retrieves forecast and historical electricity data from the
ENTSO-E API and saves the results in CSV format.

Historical data contains the following variables: total load [MW], solar generation [MW],
wind onshore generation [MW], cross-border physical flow with neighbors [MW].
Forecast data also contains energy price data [€/MWh].

The following queries are carried out in the main.py module (for Vienna, Austria):
- historical data from 2022 to the current year (included)
- day ahead forecast data for the current day, the past day and (if available) the next
day
- historical data for the past day

The results are exported as csv files.