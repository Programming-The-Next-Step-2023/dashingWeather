import unittest
import requests, json

cities = ["Amsterdam", "Cairo", "New York"]

# In the following test we determine whether our `get_coords()` function actually generates the correct coordinates of the city
# that the user types in (to 1 decimal place).

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

#city = "Amsterdam"
for city in cities:
    city = city.replace(" ", "+", 1)
    class MyTestCase(unittest.TestCase):

        def test_get_coords(self):
            coords = get_coords(city)
            if city == "Amsterdam":
                self.assertAlmostEqual(coords['lat'], 52.3676, places = 1)
                self.assertAlmostEqual(coords['lon'], 4.9041, places=1)
            elif city == "Cairo":
                self.assertAlmostEqual(coords['lat'], 30.0444, places=1)
                self.assertAlmostEqual(coords['lon'], 31.2357, places=1)
            elif city == "New York":
                self.assertAlmostEqual(coords['lat'], 40.7128, places=1)
                self.assertAlmostEqual(coords['lon'], 74.0060, places=1)

if __name__ == '__main__':
    unittest.main()
