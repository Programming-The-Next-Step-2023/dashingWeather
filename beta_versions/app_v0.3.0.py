# This is the third and final version of the app, with code that is easier to follow, a working "Go" button, a section which shows tomorrow's weather.
# I also kept the flag features commented out in this version because the flag API I was using just stopped working.

# importing packages and functions

# calculations packages
import numpy as np
import pandas as pd

# plotting/image packages
from PIL import Image
import plotly.express as px
from io import BytesIO

# API call packages
import requests
import json

# dash packages
import dash
from dash import Dash, html, dash_table, dcc, callback_context
from dash.dependencies import Input, Output, State

# time and date packages
import datetime
from datetime import timedelta, datetime, timezone
import pytz
from pytz import country_timezones

# Initialize the app
app = Dash(__name__)
app.title = "dashingWeather"

# FUNCTIONS

def units_function(unit):


    '''
    This function takes `unit` as an input (this has the options metric or imperial) and then determines which suffix to include
    when printing weather data (e.g., C or F).
    :param unit:
    :return units_of_measurement:
    '''


    temp_measurement = ""
    speed_measurement = ""
    if unit == "metric":
        temp_measurement = "°C"
        speed_measurement = "m/s"
    elif unit == "imperial":
        temp_measurement = "°F"
        speed_measurement = "mph"
    # for a weather app, standard data is probably irrelevant, so the option will be commented out
    #elif unit == "standard":
    #    temp_measurement = "°K"
    #    speed_measurement = "m/s"
    units_of_measurement = dict()
    units_of_measurement = {"temp_measurement": temp_measurement, "speed_measurement" : speed_measurement}
    return(units_of_measurement)

def get_coords(city):


    '''
    This function takes `city` as an input and uses the openweathermap API to fetch coordinates (latitude, longitude) of that city
    :param city:
    :return coords:
    '''


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

def get_current_weather(coords, unit):


    '''
    This function takes `coords` and `unit` as inputs and uses the openweathermap API to fetch the current weather
    :param coords:
    :param unit:
    :return current_weather:
    '''


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

def current_weather_to_df(current_weather, units_of_measurement):


    '''
    This function takes in the output of `get_current_weather()`, and `units_function()` and creates a subset of the
    weather data and then stores it in a pandas dataframe
    :param current_weather:
    :param units_of_measurement:
    :return weather_now:
    '''


    # calculating timezone of given city

    #tf = TimezoneFinder()
    #current_time_zone = tf.timezone_at(lng=coords['lon'], lat=coords['lat'])  # lng=longitude, lat=latitude) # returns 'Europe/Berlin'
    #current_time_zone = pytz.timezone(current_time_zone)

    current_time_zone = country_timezones(current_weather["sys"]["country"])
    current_time_zone = pytz.timezone(current_time_zone[0])
    # current_time_zone = pytz.timezone(tzwhere.tzwhere().tzNameAt(coords['lat'], coords['lon']))

    # storing current weather information in dictionary
    Conditions = np.array(["Current conditions",
                           "Temperature",
                           "Feels like",
                           "Min",
                           "Max",
                           "Sunrise",
                           "Sunset",
                           "Humidity",
                           "Wind speed",
                           "Cloudy"])
    Stats = np.array([current_weather["weather"][0]["main"],
                      str(int(np.round(current_weather["main"]["temp"])))+ " " + units_of_measurement['temp_measurement'],
                      str(int(np.round(current_weather["main"]["feels_like"])))+ " " + units_of_measurement['temp_measurement'],
                      str(int(np.round(current_weather["main"]["temp_min"])))+ " " + units_of_measurement['temp_measurement'],
                      str(int(np.round(current_weather["main"]["temp_max"])))+ " " +  units_of_measurement['temp_measurement'],

                      # timedelta is for adding two hours, because times are presented in GMT
                      str(datetime.utcfromtimestamp(current_weather["sys"]["sunrise"]).replace(tzinfo=timezone.utc).astimezone(tz=current_time_zone))[11:16],
                      str(datetime.utcfromtimestamp(current_weather["sys"]["sunset"]).replace(tzinfo=timezone.utc).astimezone(tz=current_time_zone))[11:16],

                      str(current_weather["main"]["humidity"]) + "%",
                      str(int(np.round(current_weather["wind"]["speed"]))) + " " + units_of_measurement['speed_measurement'],
                      str(int(np.round(current_weather["clouds"]["all"]))) +  "%"
                      ])
    weather_now = pd.DataFrame({"Conditions" : Conditions,
                                "Stats" : Stats})
    return(weather_now)

def get_country_flag(current_weather):


    '''
    This function fetches a country's flag from `flagsapi` based on the country data in the `current_weather` dataframe
    :param current_weather:
    :return img:
    '''


    # getting country flag
    base = 'https://flagsapi.com/'
    country =  current_weather["sys"]["country"] + "/"
    type = "flat/"
    rest = "64.png"
    url = base + country + type + rest
    image = requests.get(url)
    img = Image.open(BytesIO(image.content))
    return(img)

def get_weather_forecast(coords, unit):

    '''
    This function fetches the temperature and rain forecast for the next five days
    :param coords:
    :param unit:
    :return weather_forecast:
    '''

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

def plot_weather_forecast(weather_forecast, units_of_measurement):


    '''
    This function plots the forecast for temperature from the output of `get_weather_forecast()`.
    :param weather_forecast:
    :param units_of_measurement:
    :return fig:
    '''


    forecast = pd.DataFrame(weather_forecast["list"])
    temps = np.zeros([forecast["main"].size])
    times = pd.to_datetime(forecast["dt_txt"])
    for i in range(forecast["main"].size):
        temps[i] = forecast["main"][i]["temp"]

    # city_for_title converts text input into a "proper" format. so if a user types in "new york", plot titles will say "New York"
    # we use the replace function because an input of "new york" is actually first converted to "new+york" for data fetching
    city_for_title = city.title().replace("+", " ", 1)

    for_plot = dict()
    for_plot = ({"Temperatures" : temps, "Dates" : times})

    fig = px.line(data_frame=for_plot, x="Dates", y= "Temperatures",
                  title=str("Forecast for " + city_for_title + " temperature over the next " + str(for_plot["Dates"][for_plot["Dates"].size - 1] - for_plot["Dates"][0])[0:6]))
    fig.update_traces(line_color = "red")
    fig.update_layout(
        plot_bgcolor='white', # removing default background
        yaxis_title= str("Temperatures (" + units_of_measurement['temp_measurement'] +")"), # adding measurement to y axis title
        title_font_family=font,
    )
    fig.update_xaxes(
        title_font_family=font,
        tickfont=dict(family=font),
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        tickformat="%a \n %d %b"
    )
    fig.update_yaxes(
        title_font_family=font,
        tickfont=dict(family=font),
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        range=[np.min(temps)-15, np.max(temps)+15]
    )
    return(fig)

def plot_weather_rain(weather_forecast):


    '''
    This function plots the forecast for rain from the output of `get_weather_forecast()`.
    :param weather_forecast:
    :return fig_rain:
    '''


    forecast = pd.DataFrame(weather_forecast["list"])
    rain = dict()
    times = pd.to_datetime(forecast["dt_txt"])

    # in some cities it does not rain every week, so the fetched data just does not include a rain section
    # so this is what try and except are for, when there is no rain section we just create an empty rain section full
    # of zeros
    try:
        rain_amount = pd.DataFrame(weather_forecast["list"])["rain"]
        for i in range(len(times)):
            if type(rain_amount[i]) != dict:
                rain_amount[i] = 0
            else:
                rain_amount[i] = rain_amount[i]['3h']
    except:
        rain_amount = np.zeros(len(times))

    rain = ({"Rain": rain_amount, "Dates": times})
    # city_for_title converts text input into a "proper" format. so if a user types in "new york", plot titles will say "New York"
    # we use the replace function because an input of "new york" is actually first converted to "new+york" for data fetching
    city_for_title = city.title().replace("+", " ", 1)

    fig_rain = px.area(data_frame=rain, x="Dates", y="Rain",
                       title=str("Forecast for rain in " + city_for_title + " over the next " + str(
                           rain["Dates"][rain["Dates"].size - 1] - rain["Dates"][0])[0:6]))
    fig_rain.update_traces(line_color="#0047AB")
    fig_rain.update_layout(
        plot_bgcolor='white',
        yaxis_title=str("Expected Rain (mm)"),
        title_font_family=font, # adding measurement to y axis title
    )
    fig_rain.update_xaxes(
        title_font_family=font,
        tickfont=dict(family=font),
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        tickformat="%a \n %d %b"
    )
    fig_rain.update_yaxes(
        title_font_family=font,
        tickfont=dict(family=font),
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='white',
        range=[0, np.max(rain_amount + 0.5)]
    )
    return (fig_rain)

def world_map(world_map_metric):


    '''
    This function generates the URLs for retrieving worldwide data, based on the given metric.
    The default value is temperature.
    Output is four links, one for each quadrant of the map.

    :param world_map_metric:
    :return world_map_q1_weather, world_map_q2_weather, world_map_q3_weather, world_map_q4_weather:
    '''


    world_map_q1_weather = str("https://tile.openweathermap.org/map/" + world_map_metric + "/1/0/0.png?&appid=7c385ff223c5c8feec257ad30244934e")
    world_map_q2_weather = str("https://tile.openweathermap.org/map/" + world_map_metric + "/1/1/0.png?&appid=7c385ff223c5c8feec257ad30244934e")
    world_map_q3_weather = str("https://tile.openweathermap.org/map/" + world_map_metric + "/1/0/1.png?&appid=7c385ff223c5c8feec257ad30244934e")
    world_map_q4_weather = str("https://tile.openweathermap.org/map/" + world_map_metric + "/1/1/1.png?&appid=7c385ff223c5c8feec257ad30244934e")
    return [world_map_q1_weather, world_map_q2_weather, world_map_q3_weather, world_map_q4_weather]

def tomorrows_forecast(weather_forecast, units_of_measurement):
    '''
    This function generates a forecast for tomorrows weather, by calculating what the date will be tomorrow, then
    subsetting the relevant data from the `weather_forecast` dataframe.
    :param weather_forecast:
    :param units_of_measurement:
    :return weather_tomorrow:
    '''

    forecast_list = pd.DataFrame(weather_forecast["list"])

    # calculating tomorrow's date; we use only the first 10 parts of the string because the full thing also includes the time
    tomorrow = str(datetime.today() + timedelta(1))[0:10]

    #dates = forecast_list["dt_txt"]
    # we access the date-time in the forecast df
    # again, we use only the first 10 parts of the string because the full thing also includes the time
    #for i in range(len(forecast_list["dt_txt"])):
    #    dates[i] = str(forecast_list["dt_txt"][i])[0:10]

    forecast_list["dt_txt"] = forecast_list["dt_txt"].str.slice(stop=10)

    # need to filter out the forecasts that are not for tomorrow
    tomorrows_forecast = forecast_list.loc[(forecast_list["dt_txt"] == tomorrow)]

    # after filtering, we need to reset the index because it takes out (the rest of) today's forecast and then the index for
    # tomorrow starts not from 0, and is a different number depending on the time of day that we check. this way we reset it
    # to 0 always.
    tomorrows_forecast = tomorrows_forecast['main'].reset_index()['main']

    Conditions = np.array(['Average Temperature',
                           'Average Feels Like',
                           'Max Temp',
                           'Min Temp',
                           'Humidity'])
    Stats = np.array([str(int(np.round(np.mean([tomorrows_forecast[i]['temp'] for i in range(8)])))) +
                      units_of_measurement['temp_measurement'],
                      str(int(np.round(np.mean([tomorrows_forecast[i]['feels_like'] for i in range(8)])))) +
                      units_of_measurement['temp_measurement'],
                      str(int(
                          np.round(np.ndarray.max(np.array([tomorrows_forecast[i]['temp_max'] for i in range(8)]))))) +
                      units_of_measurement['temp_measurement'],
                      str(int(
                          np.round(np.ndarray.min(np.array([tomorrows_forecast[i]['temp_min'] for i in range(8)]))))) +
                      units_of_measurement['temp_measurement'],
                      str(int(np.round(np.mean([tomorrows_forecast[i]['humidity'] for i in range(8)])))) + "%"
                      ])
    weather_tomorrow = pd.DataFrame({"Conditions": Conditions,
                                     "Stats": Stats})
    return (weather_tomorrow)

# RUNNING FUNCTIONS

# this is how things are set when we first open the app, where the user can change city and metric
city = "Amsterdam"
now_showing = "Showing current weather for " + city
unit = "metric"
font = "Baskerville"
world_map_metric = "temp_new"

# the replace function is used so that inputs such as "new york" are converted to "new+york" for API call
city = city.replace(" ", "+", 1)
city_for_title = city.title().replace("+", " ", 1)

# this is the first run of all functions, which occurs as soon as the app is launched.
# they then re-run depending on user input (clicking button/radio buttons/drop down menu item)
units_of_measurement = units_function(unit)
coords = get_coords(city)
current_weather = get_current_weather(coords, unit)
current_weather_df = current_weather_to_df(current_weather, units_of_measurement)
current_weather_df = current_weather_df.to_dict('records')
#img = get_country_flag(current_weather)
weather_forecast = get_weather_forecast(coords, unit)
fig = plot_weather_forecast(weather_forecast, units_of_measurement)
fig_rain = plot_weather_rain(weather_forecast)
world_map_metrics = world_map(world_map_metric)
weather_tomorrow = tomorrows_forecast(weather_forecast, units_of_measurement)
weather_tomorrow = weather_tomorrow.to_dict('records')

# App layout
# here we design the app layout, i.e., where everything will be placed and what it will look like
app.layout = html.Div([
    html.Div(children=[
        # first column
        html.Div(children=[
            # input city prompt space
            html.Div([html.P(children="Which city do you live in?", style = {'font-family':font, "font-size": "20px", 'width': '40vh'}),
                      dcc.Input(id="city", type="text", placeholder="Enter city name", style = {'font-family':font, "font-size": "20px"}),
                      # breaks
                      html.Br(), html.Br(),
                      html.Button('Go', id = "button", style = {'font-family':font, "font-size": "16px"}),
                      html.Br(), html.Br()],
                     style = {'textAlign': 'center', 'width': '40vh',
                              "border":"2px black solid",}),
            html.Br(),

            # input unit prompt space
            html.Div([html.P(children="Choose a system of measurement",
                             style = {'font-family':font, "font-size": "18px"}),
                      dcc.RadioItems(id = "unit",
                                     options = [{"label": 'Metric', "value" : "metric"},
                                                {"label": 'Imperial', "value" : "imperial"}],
                                     value = 'metric', # the default value, sorry Americans
                                     inline = True,
                                     style = {'font-family':font, "font-size": "16px"}),
                      html.Br(),], style = {'textAlign': 'center',
                                            "border":"2px black solid"}),
            html.Br(),

            # current weather + flag display (if it works)
            html.Div(children = [
                # flag display
                #html.Img(id="flag", src=img, style={'width': '3.0vh', 'height': '3vh'}),
                html.P(id = "showing_weather_for", children = now_showing,
                       style = {'textAlign': 'center', "font-family" : font, "font-size" : "16px"}),

                # today's weather data table
                dash_table.DataTable(id="current_weather_df",
                                     data=current_weather_df,
                                     page_size=10,
                                     fill_width=True,
                                     style_cell={'textAlign': 'center', 'font-family':font},
                                     style_data={'width': '125px','height': '20px'})],
                style = {'textAlign': 'center', "border":"2px black solid"})],
            style={'display': 'inline-block', 'horizontal-align' : 'center', 'vertical-align': 'top','margin-left': '3vw', 'margin-top': '3vw'}), # div style

        # second column
        html.Div(id = "graph_column", children=[
            # temperature plot
            html.Div([dcc.Graph(id="forecast_graph",
                                figure=fig,
                                style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'})]),
            html.Br(),

            # rain plot
            html.Div([dcc.Graph(id="rain_graph",
                                figure=fig_rain,
                                style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'})]),
            html.Br()],
                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '2vw',
                        'margin-top': '3vw',"border":"2px black solid"}),

        # third column
        html.Div(children=[html.Div(children = [
            dcc.Dropdown(id = "world_map", options = [{"label" : 'Temperature', "value" : "temp_new"},
                                                      {"label" : 'Wind', "value" : "wind_new"},
                                                      {"label" : "Clouds", "value" : "clouds_new"},
                                                      {"label" : "Precipitation", "value" : "precipitation_new"},
                                                      {"label" : "Pressure", "value" : "pressure_new"}],
                         value = 'temp_new',
                         style = {'font-family':font, "font-size": "16px", 'top': '0vh'}),

            # world + weather map
            # here we have to overlap two maps: a world map and a world weather map, where the world weather map
            # is on top. so we tackle these two maps one quadrant at a time, starting from the top two
            # (left, then right).

            # top
            html.Img(src="https://tile.openstreetmap.org/1/0/0.png",
                     style={'position': 'absolute','top': '5vh', 'left': '0vh','width': '20vh', 'height': '20vh'}),
            html.Img(id = "world_map_q1_weather", src=world_map_metrics[0],
                     style={'position': 'absolute','top': '5vh', 'left': '0vh','width': '20vh', 'height': '20vh'}),
            html.Img(src="https://tile.openstreetmap.org/1/1/0.png",
                     style={'position': 'absolute','top': '5vh', 'left': '20vh','width': '20vh', 'height': '20vh'}),
            html.Img(id = "world_map_q2_weather",src=world_map_metrics[1],
                     style={'position': 'absolute', 'top': '5vh', 'left': '20vh','width': '20vh', 'height': '20vh'}),

            # bottom
            html.Img(src="https://tile.openstreetmap.org/1/0/1.png",
                     style={'position': 'absolute', 'top': "25vh", 'left': '0vh', 'width': '20vh','height': '20vh'}),
            html.Img(id = "world_map_q3_weather",src=world_map_metrics[2],
                     style={'position': 'absolute', 'top': '25vh', 'left': '0vh', 'width': '20vh','height': '20vh'}),
            html.Img(src="https://tile.openstreetmap.org/1/1/1.png",
                     style={'position': 'absolute', 'top': '25vh', 'left': '20vh', 'width': '20vh','height': '20vh'}),
            html.Img(id = "world_map_q4_weather",src=world_map_metrics[3],
                     style={'position': 'absolute', 'top': '25vh', 'left': '20vh', 'width': '20vh','height': '20vh'}),
        ]),
            # tomorrow's weather
            html.Div([
                html.P(id = "weather_tomorrow_title", children = "Tomorrow's weather",
                       style = {'textAlign': 'center', "font-family" : font, "font-size" : "16px"}),
                dash_table.DataTable(id="tomorrows_forecast",
                                     data=weather_tomorrow,
                                     page_size=10,
                                     fill_width=True,
                                     style_cell={'textAlign': 'center', 'font-family': font},
                                     style_data={'width': '140px', 'height': '20px'})],
                     style = {'position': 'absolute', 'top' : "48vh", "left" : "0vh",
                              "border":"2px black solid", "width" : "40vh"}),

            # my name + credentials
            html.Div(children = [
                html.P(["Created by Mohammad Hamdan", html.Br(), "@the_mhamdan on Twitter"])],
                style = {"font-family" : font, "font-size" : "14px", "color" : "#8B8B8B",
                         'position': 'absolute', 'top' : "79vh", "text-align" : "left"})],
            style={'display': 'inline-block', 'textAlign': 'center','position': 'relative', 'width': '40vh',
                   'vertical-align': 'top', 'margin-left': '2vw', 'margin-top': '3vw', 'height' : '45vh',
                   "border":"2px black solid", 'backgroundColor':'black'
                   })],
    className='row')])

# Below are all app.callbacks, which make the app interactive (when user changes inputs, new outputs are generated)

# refreshing only when button is clicked
# updating graphs and tables after changing city
@app.callback(
    [Output(component_id="current_weather_df",
            component_property="data",
            allow_duplicate=True),
     Output(component_id="forecast_graph",
            component_property="figure",
            allow_duplicate=True),
     Output(component_id="rain_graph",
            component_property="figure",
            allow_duplicate=True),
     Output(component_id="showing_weather_for",
            component_property="children",
            allow_duplicate=True),
     Output(component_id="tomorrows_forecast",
            component_property="data",
            allow_duplicate=True
            ),
     ],
    [Input(component_id='city',
          component_property='value'),
     Input('button', "n_clicks")],
    [State("city", "value")],
    prevent_initial_call='initial_duplicate'
)

def update_city(selection, n_clicks, n_clicks_update):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'button' in changed_id:

        global city
        city = city.capitalize().replace(" ", "+", 1)

        if selection:
            city = selection

        coords = get_coords(city)
        current_weather = get_current_weather(coords, unit)
        current_weather_df = current_weather_to_df(current_weather, units_of_measurement)
        current_weather_df = current_weather_df.to_dict('records')
        #img = get_country_flag(current_weather)
        weather_forecast = get_weather_forecast(coords, unit)
        fig = plot_weather_forecast(weather_forecast, units_of_measurement)
        fig_rain = plot_weather_rain(weather_forecast)
        now_showing = "Showing current weather for " + city
        now_showing = now_showing.title()
        weather_tomorrow = tomorrows_forecast(weather_forecast, units_of_measurement)
        weather_tomorrow = weather_tomorrow.to_dict('records')

        return [current_weather_df, fig, fig_rain, now_showing, weather_tomorrow]

# updating temperature graph and table after changing unit
@app.callback(
    [Output(component_id="current_weather_df",
            component_property="data"),
     Output(component_id="forecast_graph",
            component_property="figure"),
     Output(component_id="tomorrows_forecast",
            component_property="data"),
     ],
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
    fig = plot_weather_forecast(weather_forecast, units_of_measurement)
    weather_tomorrow = tomorrows_forecast(weather_forecast, units_of_measurement)
    weather_tomorrow = weather_tomorrow.to_dict('records')
    return[current_weather_df, fig, weather_tomorrow]

# updating world map based on user selection from dropdown
@app.callback(
    [Output(component_id="world_map_q1_weather",
            component_property="src",
            ),
     Output(component_id="world_map_q2_weather",
            component_property="src",
            ),
     Output(component_id="world_map_q3_weather",
            component_property="src",
            ),
     Output(component_id="world_map_q4_weather",
            component_property="src",
            )],
    Input(component_id='world_map',
          component_property='value'),
)

def update_map(selection):
    global world_map_metric
    world_map_metric = world_map_metric

    if selection:
        world_map_metric = selection

    world_map_metrics = world_map(world_map_metric)

    return world_map_metrics

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
