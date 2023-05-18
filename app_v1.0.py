# This is the first version of the app, with minimal style changes and basic functionality only

# importing packages and functions

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import requests
import json
from PIL import Image
import requests
from io import BytesIO
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import calendar

# Initialize the app
app = Dash(__name__)

# FUNCTIONS

# units_function() takes `unit` (metric/imperial/standard) as an input, and then determines which suffix to include
# when printing weather data
def units_function(unit):
    temp_measurement = ""
    speed_measurement = ""
    if unit == "metric":
        temp_measurement = "°C"
        speed_measurement = "km/h"
    elif unit == "imperial":
        temp_measurement = "°F"
        speed_measurement = "mph"
    elif unit == "standard":
        temp_measurement = "°K"
        speed_measurement = "km/h"
    units_of_measurement = dict()
    units_of_measurement = {"temp_measurement": temp_measurement, "speed_measurement" : speed_measurement}
    return(units_of_measurement)

# get_coords() uses the openweathermap API to fetch coordinates (latitude, longitude) of a city based on its name
# which comes from user input
def get_coords(city):
    # getting coordinates from city name and storing them in a dictionary
    base = 'http://api.openweathermap.org/geo/1.0/direct?q='
    api_key = '&appid=7c385ff223c5c8feec257ad30244934e'
    url = base + city + api_key

    response_API = requests.get(url)
    data = response_API.text
    parse_json = json.loads(data)

    coords = dict()
    coords['lat'] = parse_json[0]['lat']
    coords['lon'] = parse_json[0]['lon']

    return(coords)

# get_current_weather() fetches the current weather using given coordinates
def get_current_weather(coords, unit):
    # getting current weather information from coordinates
    base = "https://api.openweathermap.org/data/2.5/weather?"
    lat = "lat=" + str(coords['lat'])
    lon = "&lon=" + str(coords['lon'])
    units = "&units=" + unit
    api_key = "&appid=7c385ff223c5c8feec257ad30244934e"
    url = str(base + lat + lon + units + api_key)

    response_API = requests.get(url)
    data = response_API.text
    current_weather = json.loads(data)

    return(current_weather)

# current_weather_to_df takes a subset of the weather data and stores it in a pandas df
def current_weather_to_df(current_weather, units_of_measurement):
    # storing current weather information in dictionary
    Conditions = np.array(["Current conditions",
                           "Temperature",
                           "Feels like",
                           "Min",
                           "Max",
                           "Humidity",
                           "Wind speed",
                           "Cloudy"])
    Stats = np.array([current_weather["weather"][0]["main"],
                      str(int(np.round(current_weather["main"]["temp"])))+ " " + units_of_measurement['temp_measurement'],
                      str(int(np.round(current_weather["main"]["feels_like"])))+ " " + units_of_measurement['temp_measurement'],
                      str(int(np.round(current_weather["main"]["temp_min"])))+ " " + units_of_measurement['temp_measurement'],
                      str(int(np.round(current_weather["main"]["temp_max"])))+ " " +  units_of_measurement['temp_measurement'],
                      str(current_weather["main"]["humidity"]) + "%",
                      str(int(np.round(current_weather["wind"]["speed"]))) + " " + units_of_measurement['speed_measurement'],
                      str(int(np.round(current_weather["main"]["temp"]))) + " " +  units_of_measurement['temp_measurement']
                      ])
    weather_now = pd.DataFrame({"Conditions" : Conditions,
                                "Stats" : Stats})
    return(weather_now)

# get_country_flag() fetches a country's flag from flagsapi based on the country data outputted in get_current_weather()
def get_country_flag(current_weather):
    # getting country flag
    base = 'https://flagsapi.com/'
    country =  current_weather["sys"]["country"] + "/"
    type = "flat/"
    rest = "64.png"
    url = base + country + type + rest
    image = requests.get(url)
    img = Image.open(BytesIO(image.content))
    return(img)

# get_weather_forecast gets the forecast over the next five days
def get_weather_forecast(coords, unit):
    # getting forecast data
    base = 'https://api.openweathermap.org/data/2.5/forecast?'
    lat = "lat=" + str(coords['lat'])
    lon = "&lon=" + str(coords['lon'])
    units = "&units=" + unit
    api_key = "&appid=7c385ff223c5c8feec257ad30244934e"
    url = str(base + lat + lon + units + api_key)

    response_API = requests.get(url)
    data = response_API.text
    weather_forecast = json.loads(data)

    return(weather_forecast)

# plot_weather_forecast plots the forecast for temperature as outputted in the previous function
def plot_weather_forecast(weather_forecast):
    forecast = pd.DataFrame(weather_forecast["list"])
    temps = np.zeros([forecast["main"].size])
    times = pd.to_datetime(forecast["dt_txt"])
    for i in range(forecast["main"].size):
        temps[i] = forecast["main"][i]["temp"]

    # city_for_title converts text input into a "proper" format. so if a user types in "new york", plot titles will say "New York"
    # we use the replace function because an input of "new york" is actually first converted to "new+york" for JSON retrieval
    city_for_title = city.title().replace("+", " ", 1)

    for_plot = dict()
    for_plot = ({"Temperatures" : temps, "Dates" : times})

    fig = px.line(data_frame=for_plot, x="Dates", y="Temperatures",
                  title=str("Forecast for " + city_for_title + " temperature over the next " + str(for_plot["Dates"][for_plot["Dates"].size - 1] - for_plot["Dates"][0])[0:6]))
    fig.update_traces(line_color = "red")
    fig.update_layout(
        plot_bgcolor='white'
    )
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        tickformat="%a \n %d %b"
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        range=[np.min(temps)-10, np.max(temps)+10]
    )
    return(fig)

# plot_weather_rain plots the forecast for rain over the next five days
def plot_weather_rain(weather_forecast):
    forecast = pd.DataFrame(weather_forecast["list"])
    rain = dict()
    times = pd.to_datetime(forecast["dt_txt"])

    rain_amount = pd.DataFrame(weather_forecast["list"])["rain"]

    for i in range(len(rain_amount)):
        if type(rain_amount[i]) != dict:
            rain_amount[i] = 0
        else:
            rain_amount[i] = rain_amount[i]['3h']

    rain = ({"Rain": rain_amount, "Dates": times})
    # city_for_title converts text input into a "proper" format. so if a user types in "new york", plot titles will say "New York"
    # we use the replace function because an input of "new york" is actually first converted to "new+york" for JSON retrieval
    city_for_title = city.title().replace("+", " ", 1)

    fig_rain = px.area(data_frame=rain, x="Dates", y="Rain",
                       title=str("Forecast for rain in " + city_for_title + " over the next " + str(
                           rain["Dates"][rain["Dates"].size - 1] - rain["Dates"][0])[0:6]))
    fig_rain.update_traces(line_color="#0047AB")
    fig_rain.update_layout(
        plot_bgcolor='white'
    )
    fig_rain.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        tickformat="%a \n %d %b"
    )
    fig_rain.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white'
    )
    return (fig_rain)

# running functions
city = "Dublin"
unit = "imperial"

# the replace function is used so that inputs such as "new york" are converted to "new+york" for JSON retrieval
city = city.replace(" ", "+", 1)

units_of_measurement = units_function(unit)
coords = get_coords(city)
current_weather = get_current_weather(coords, unit)
current_weather_df = current_weather_to_df(current_weather, units_of_measurement)
current_weather_df = current_weather_df.to_dict('records')
img = get_country_flag(current_weather)
weather_forecast = get_weather_forecast(coords, unit)
fig = plot_weather_forecast(weather_forecast)
fig_rain = plot_weather_rain(weather_forecast)

# App layout
app.layout = html.Div([
# first row
    html.Div(children=[

        # first column of first row
        html.Div(children=[

            html.P(children="Let's find out if you'll need a poncho today",
                   ),
            html.Br(),
            dcc.Input(id="city", type="text", placeholder="Enter city name",
                      ),
            html.Br(), html.Br(),
            html.Div([html.Img(id="flag",
                               src=img,
                               style={'width': '3.5vh',
                                      'height': '3vh'
                                      })], style = {'textAlign': 'center'}),
            html.P(children="Pick a system of measurement",
                   ),
            html.Br(),
            dcc.RadioItems(id = "unit", options = [{"label": 'Metric', "value" : "metric"},
                                                   {"label": 'Imperial', "value" : "imperial"},
                                                   {"label": 'Standard', "value" : "standard"}],
                           value = 'metric',
                           inline = True,
                           ),
            html.Br(), html.Br(), html.Br(),
            dash_table.DataTable(id="current_weather_df",
                                           data=current_weather_df,
                                           page_size=8, fill_width=False,
                                           style_cell={'textAlign': 'left',
                                 }
                                 ),
                      html.Br(), html.Br(),

        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'}),
        html.Div(children=[
            html.Div([dcc.Graph(id="forecast_graph", figure=fig,
                                style={'width': '90vh', 'height': '40vh', 'display': 'inline-block'})]),
            html.Div([dcc.Graph(id="rain_graph", figure=fig_rain,
                                style={'width': '90vh', 'height': '40vh', 'display': 'inline-block'})]),
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'})],
    className='row')])

# updating graphs and table after changing city
@app.callback(
    [Output(component_id="current_weather_df",
            component_property="data",
            allow_duplicate=True),
     Output(component_id="forecast_graph",
            component_property="figure",
            allow_duplicate=True),
     Output(component_id="rain_graph",
            component_property="figure",
            allow_duplicate=True)],
    Input(component_id='city',
          component_property='value'),
    prevent_initial_call='initial_duplicate'
)

def update_city(selection):
    global city
    city = city.capitalize().replace(" ", "+", 1)

    if selection:
        city = selection

    coords = get_coords(city)
    current_weather = get_current_weather(coords, unit)
    current_weather_df = current_weather_to_df(current_weather, units_of_measurement)
    img = get_country_flag(current_weather)
    weather_forecast = get_weather_forecast(coords, unit)
    fig = plot_weather_forecast(weather_forecast)
    fig_rain = plot_weather_rain(weather_forecast)
    return [current_weather_df.to_dict('records'), fig, fig_rain]

# updating flag after changing city
@app.callback(
    Output(component_id="flag",
           component_property= "src"),
    Input(component_id='city',
          component_property='value')
)

def update_flag(selection):
    global city
    city = city.capitalize().replace(" ", "+", 1)

    if selection:
        city = selection

    coords = get_coords(city)
    current_weather = get_current_weather(coords, unit)
    current_weather_df = current_weather_to_df(current_weather, units_of_measurement)
    img = get_country_flag(current_weather)
    return img


# updating temperature graph and table after changing unit
@app.callback(
    [Output(component_id="current_weather_df",
            component_property="data"),
     Output(component_id="forecast_graph",
            component_property="figure")],
    Input(component_id='unit',
          component_property='value')
)

def update_unit(selection):
    global unit
    unit = unit

    if selection:
        unit = selection

    units_of_measurement = units_function(unit)
    current_weather = get_current_weather(coords, unit)
    current_weather_df = current_weather_to_df(current_weather, units_of_measurement)
    current_weather_df = current_weather_df.to_dict('records')
    weather_forecast = get_weather_forecast(coords, unit)
    fig = plot_weather_forecast(weather_forecast)
    return[current_weather_df, fig]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

