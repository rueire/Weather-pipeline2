# const url = "https://api.open-meteo.com/v1/forecast";

# pip install openmeteo-requests
# pip install requests-cache retry-requests numpy pandas

from turtle import left
from urllib import response
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import date, timedelta

#set to check tomorrow's forecast
tomorrow = date.today() + timedelta(days=1)
tomorrow_str = tomorrow.isoformat()

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

# EXTRACT
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 60.1699,
	"longitude": 24.9384,
	"hourly": "temperature_2m,apparent_temperature",
    "timezone": 'Europe/Helsinki',
    'start_date': tomorrow_str,
    'end_date': tomorrow_str,
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# TRANSFORM
# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()

#unit='s' = seconds, range makes sure hours are in order and that nothing is missing
hourly_df= pd.DataFrame({
    'time': pd.date_range(start=pd.to_datetime(hourly.Time(),unit='s', utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit='s', utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive='left'
    ),
    'temperature_2m' : hourly_temperature_2m,
    'apparent_temperature': hourly_apparent_temperature
})

# time as index
hourly_df = hourly_df.set_index('time')

# LOAD
print("\nHourly data\n", hourly_df)