# dashingWeather

I will be creating a weather app for the course "Programming: The Next Step".

This app will be built using `Dash` and will fetch information using the free API of `openweathermap.org`. It will include various funtionalities such as displaying current weather conditions (incl. temperature, humidity, wind speed), as well as a forecast for temperature and rain over the next few days (max up to 5), number of days can be user customized.

A weather app created by using `Dash`

Version 0.1.0:

The `Dash` app can now load current weather conditions and a five-day forecast for temperature and rain based on two user inputs: the city which they wish to view and the measurement system they wish to view information in.

The user basically only has to type in the city name and the app fetches (a lot of) information from `openweatherapi`, and then this weather is either presented in a table, or a graph, or used to fetch flag information.

This version is mostly functional, however there are some known errors and missing features which will be implemented soon:
-	Error: Cities where no rain is expected: the fetched data does not include a “rain” section, rather than having something equivalent to rain = 0. So, the app can then only present the existing data and displays an error for the rain forecast graph.
-	Error: A button needs to be added, along with preventing the app from updating unless this button is clicked. For now, when typing a city name the user is met with an error while typing name because the app attempts to fetch data with a partial city name.
-	Missing feature: user adjustable forecast length. 
-	Missing feature: more weather metrics, such as sunrise and sunset times
-	Format: present things more properly, e.g., have borders, and better prompts

Version 0.2.0:

This version includes a fix for the rain error from version 1.0, adds more weather metrics and improves the layout of the app. I have decided not to include a user adjustable weather forecast length, since it seems to be not a super useful or interesting feature given the fact that the forecast included is already quite short-length, but in version 3.0 I will include a "tomorrow's weather" section as that can be quite useful. This version also includes a world-wide weather map with user adjustable metrics, so the user can choose to see the temperatures, wind or clouds (for example) around the world. 

In the next version:
- Button still needs to be added
- Weather tomorrow
- Might need to remove the flag feature, as there seems to be an error originating with the API provider

Version 0.3.0:

This is the final version of the app, but will probably continue to recieve minor changes until the end of the course. It includes a "tomorrow's weather" section, a functional "Go" button, new icons and other layout changed - as well as a dynamic icon: a flag (I have opted to use a different API call from a more reliable source, so hopefully this feature will stay).
Due to continous small changes, 3.0 might not be the final 3.x version on this branch, so please refer to the latest version available.
