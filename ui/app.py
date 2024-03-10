
import requests

from streamlit_folium import folium_static
import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import datetime


'''
# Advanced Power Prediction
(v0.1)
'''

# create a sidebar in order to take user inputs
st.sidebar.markdown(f"""
    # User Input
    """)

prediction_date = st.sidebar.date_input(
                            label='Power prediction date',
                            value=datetime.date(2021, 7, 6),
                            min_value=datetime.date(2020, 1, 1),
                            max_value=datetime.date(2022, 12, 30),
                            )
# predicition_time = st.sidebar.time_input(
#                             label='Power prediction time',
#                             value=datetime.time(0, 00),
#                             step=3600)
input_prediction_date = f"{prediction_date} 00:00:00"
# st.sidebar.write(input_prediction_date)


locations = st.sidebar.expander("Available locations")
# days_to_display = st.sidebar.slider('Select the number of past data to display', 1, 10, 5)


location = locations.radio("Locations", ["Berlin - Tempelhof", "Berlin - Tegel", "Berlin - Schönefeld"])


# make api call
# make api call
base_url = "http://127.0.0.1:8000"

# model
params_model ={
    'input_date':input_prediction_date,
    'n_days': 2,
    'power_source': 'pv'
    }

endpoint_model = "/baseline_yesterday"
url_model= f"{base_url}{endpoint_model}"
response_model = requests.get(url_model, params_model).json()

# baseline
params_baseline ={
    'input_date':input_prediction_date,
    'n_days': 2,
    'power_source': 'pv'
    }

endpoint_baseline = "/baseline_yesterday"
url_baseline= f"{base_url}{endpoint_baseline}"
response_baseline = requests.get(url_baseline, params_baseline).json()

# data
params_data ={
    'input_date':input_prediction_date,
    'n_days': 10,
    'power_source': 'pv'
    }

endpoint_data = "/extract_data"
url_data = f"{base_url}{endpoint_data}"
response_data = requests.get(url_data, params_data).json()


# Main Panel
# Write name of chosen location
st.write(f"**Chosen location:** :red[{location}]")


# set-up 4 DatFrames according to input date and type of model
X = pd.DataFrame(response_data.get(input_prediction_date)['days_before'])
y = pd.DataFrame(response_data.get(input_prediction_date)['day_after'])
y_baseline = pd.DataFrame(response_baseline.get(input_prediction_date))
y_predicted = pd.DataFrame(response_model.get('dataframe to predict'))

# convert date columns to datetime object
X.date = pd.to_datetime(X.date,utc=True)
y.date = pd.to_datetime(y.date, utc=True)
y_baseline.date = pd.to_datetime(y_baseline.date, utc=True) + datetime.timedelta(days=1)

# Matplotlib pyplot of the PV data
fig, ax = plt.subplots(sharex=True, sharey=True)
ax.plot(X.date, X.power_source, label='current production data')
ax.plot(y.date, y.power_source, label='true production')
ax.plot(y_baseline.date, y_baseline.power_source, label='baseline estimate')
plt.ylim(0,1)
plt.legend()
st.pyplot(fig)


# Metrics
mean_training = X.power_source.mean()
mean_baseline = y_baseline.power_source.mean()
mean_diff = mean_baseline - mean_training

# Trick to use 4 columns to display the metrics centered below graph
col1, col2, col3, col4 = st.columns(4)
col2.metric("Training", round(mean_training,3), "")
col3.metric("Predicted", round(mean_baseline,3), round(mean_diff,3))


# Map with the location
coordinates = {
            'Berlin - Tempelhof':{'lat':52.4821,'lon':13.3892},
            'Berlin - Tegel':{'lat':52.5541,'lon':13.2931},
            'Berlin - Schönefeld':{'lat':52.3733,'lon':5064},
               }

map =folium.Map(
    location=[coordinates[location]['lat'],
              coordinates[location]['lon']],
    zoom_start=13)
folium.Marker([coordinates[location]['lat'], coordinates[location]['lon']],
              popup=location,
              icon=folium.Icon(color='red')).add_to(map)
folium_static(map)
