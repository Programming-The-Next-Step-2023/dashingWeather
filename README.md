# dashingWeather
A weather app created by using `Dash`

Version 1.0:

The `Dash` app can now load current weather conditions and a five-day forecast for temperature and rain based on two user inputs: the city which they wish to view and the measurement system they wish to view information in.

The user basically only has to type in the city name and the app fetches (a lot of) information from `openweatherapi`, and then this weather is either presented in a table, or a graph, or used to fetch flag information.

This version is mostly functional, however there are some known errors and missing features which will be implemented soon:
-	Error: Cities where no rain is expected: the fetched data does not include a “rain” section, rather than having something equivalent to rain = 0. So, the app can then only present the existing data and displays an error for the rain forecast graph.
-	Error: A button needs to be added, along with preventing the app from updating unless this button is clicked. For now, when typing a city name the user is met with an error while typing name because the app attempts to fetch data with a partial city name.
-	Missing feature: user adjustable forecast length. 
-	Missing feature: more weather metrics, such as sunrise and sunset times
-	Format: present things more properly, e.g., have borders, and better prompts

![image](https://github.com/Programming-The-Next-Step-2023/dashingWeather/assets/132884849/7bb067c3-7523-40fb-9c17-e690fd56df68)
