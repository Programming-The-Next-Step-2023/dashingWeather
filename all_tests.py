import unittest
import requests, json
import numpy as np
import pandas as pd

# this is the list of cities used for the test. input is deliberately written in a wonky way to show that the
# function can still properly retrieve the name of the desired city
cities = ["amstErdam", "cAiro", "new york", "lOs angeles", "mOntreal", "agios dimitrios",
          "the haGue", "dar El sAlam", "hibiscus coast", "kingston upon hull"]

def city_name_correct(city):
    city = city.replace(" ", "+", 2)
    city_for_title = city.title().replace("+", " ", 2)
    return(city, city_for_title)

def get_coords(city):


    '''
    This function takes `city` as an input and uses the openweathermap API to fetch coordinates (latitude, longitude) of that city
    :param city:
    :return coords:
    '''

    base = 'http://api.openweathermap.org/geo/1.0/direct?q='
    api_key = '&appid=7c385ff223c5c8feec257ad30244934e'
    url = base + city_name_correct(city)[0] + api_key

    response_API = requests.get(url)
    data = response_API.text
    parse_json = json.loads(data)

    coords = dict()
    coords['lat'] = parse_json[0]['lat']
    coords['lon'] = parse_json[0]['lon']

    return(coords)

def no_rain(weather_forecast_list, times):

    '''
    In some cities it does not rain every week, so the fetched data just does not include a rain section.
    Using this function we make sure that when there is no rain section we create rain data where the values are all zeros.

    :param weather_forecast_list:
    :return:
    '''

    try:
        rain_amount = pd.DataFrame(weather_forecast_list)["rain"]
        for i in range(len(times)):
            if type(rain_amount[i]) != dict:
                rain_amount[i] = 0
            else:
                rain_amount[i] = rain_amount[i]['3h']
    except:
        rain_amount = np.zeros(len(times))

    return(rain_amount)

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

for city in cities:
    
    class MyTestCase(unittest.TestCase):

        '''
        in these tests we check whether our input conversion, geolocator and rain checker functions work
        1. when a user inputs a city name (e.g., "new york"), it needs to be converted into a plotting format
        ("New York"), and a url format ("new+york").
        2. weather retrieval can only be done using coordinates, but users will input city names, so we need
        to check that our coordinate retrieval works
        3. when fetching rain data, if it will not rain in the 5 day forecast, the API call does not return anything.
        however this is a problem when plotting this data, so we test our function that then generates an array with
        0 values which can be used for plotting.

        The fourth and final test is a test of time data, we retrieve data in a datetime format, then convert it to string
        for plotting, so for each city we check where the year and month after manipulation correspond to May or June 2023.
        '''

        def test_city_names_coords(self):

            test = city_name_correct(city)
            coords = get_coords(city)
            forecast = pd.DataFrame(get_weather_forecast(coords, "metric")["list"])
            times = pd.to_datetime(forecast["dt_txt"])
            rain_amount = no_rain(get_weather_forecast(coords, "metric")["list"], times)

            if city == "amstErdam":
                self.assertEqual(test[0], "amsterdam")
                self.assertEqual(test[1], "Amsterdam")

                self.assertAlmostEqual(coords['lat'], 52.3676, places=1)
                self.assertAlmostEqual(coords['lon'], 4.9041, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"]) # the app will only be used tested in may/june 2023

            elif city == "cAiro":
                self.assertEqual(test[0], "cairo")
                self.assertEqual(test[1], "Cairo")

                self.assertAlmostEqual(coords['lat'], 30.0444, places=1)
                self.assertAlmostEqual(coords['lon'], 31.2357, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "new york":
                self.assertEqual(test[0], "new+york")
                self.assertEqual(test[1], "New York")

                self.assertAlmostEqual(coords['lat'], 40.7128, places=1)
                self.assertAlmostEqual(coords['lon'], -74.0060, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "lOs angeles":
                self.assertEqual("los+angeles", test[0])
                self.assertEqual("Los Angeles", test[1])

                self.assertAlmostEqual(coords['lat'], 34.0522, places=1)
                self.assertAlmostEqual(coords['lon'], 118.2437, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "mOntreal":
                self.assertEqual("montreal", test[0])
                self.assertEqual("Montreal", test[1])

                self.assertAlmostEqual(coords['lat'], 45.5019, places=1)
                self.assertAlmostEqual(coords['lon'], 73.5674, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "agios dimitrios":
                self.assertEqual("agios+dimitrios", test[0])
                self.assertEqual("Agios Dimitrios", test[1])

                self.assertAlmostEqual(coords['lat'], 37.9357, places=1)
                self.assertAlmostEqual(coords['lon'], 23.7295, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "the haGue":
                self.assertEqual("the+hague", test[0])
                self.assertEqual("The Hague", test[1])

                self.assertAlmostEqual(coords['lat'], 52.0705, places=1)
                self.assertAlmostEqual(coords['lon'], 4.3007, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "dar El sAlam":
                self.assertEqual("dar+el+salam", test[0])
                self.assertEqual("Dar El Salam", test[1])

                self.assertAlmostEqual(coords['lat'], 6.7924, places=1)
                self.assertAlmostEqual(coords['lon'], 39.2083, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "hibiscus coast":
                self.assertEqual("hibiscus+coast", test[0])
                self.assertEqual("Hibiscus Coast", test[1])

                self.assertAlmostEqual(coords['lat'], -36.6058, places=1)
                self.assertAlmostEqual(coords['lon'], 174.6978, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

            elif city == "kingston upon hull":
                self.assertEqual("kingston+upon+hull", test[0])
                self.assertEqual("Kingston Upon Hull", test[1])

                self.assertAlmostEqual(coords['lat'], 53.7404, places=1)
                self.assertAlmostEqual(coords['lon'], -0.3262, places=1)

                self.assertEqual(len(rain_amount), 40)

                for i in range(len(times)):
                    self.assertTrue(str(times[i])[0:7] in ["2023-05", "2023-06"])

if __name__ == '__main__':
    unittest.main()
