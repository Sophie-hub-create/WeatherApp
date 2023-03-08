from api_keys import api_keys
import requests
import gzip
import json
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen

weather_images = {
    800: "pics_weather/sun.png",
    801: "pics_weather/weather4.png",
    803: "pics_weather/cloudy.png",
    599: "pics_weather/snow.png",
    532: "pics_weather/rainy.png",
    504: "pics_weather/sunnyrainy.png",
    200: "pics_weather/gewitter.png",
    "default": "pics_weather/sunnycloudy.png"
    }

weather_advice = {
        599: "Don't forget your gloves",
        532: "Don't forget your umbrella",
        504: "Don't forget your umbrella",
        200: "Take care of yourself",
        "default": "Have a good day"
    }
    
class WindowManager(ScreenManager):
    pass


class ForecastWindow(Screen):
    pass


class PopUpWindow(Popup):
    pass


class MainWindow(Screen):
    pass


class showWeatherApp(App):
    

    Window.clearcolor = (0.94, 0.87, 0.706)
    

    def on_start(self):
        """method ensures how screen looks like on start"""
        self.forecast_weather_data('Berlin')
        self.current_weather_data('Berlin')

    def datetime(self, city: str) -> str:
        """
        method for setting Weekday and time of a given city
        
        :param city: The name of the city the user searches for
        :return: a string of the formatted datetime (day, hour:minute)
        """
        api_url = f'https://api.api-ninjas.com/v1/worldtime?city={city}'
        response = requests.get(
            api_url, headers={'X-Api-Key': api_keys['worldtime']})
        datetime_data = response.json()
        if response.status_code == requests.codes.ok:
            # get day, hour, minute from data und format (Monday, 12:05)
            day = datetime_data["day_of_week"]
            hour = datetime_data["hour"]
            minute = datetime_data["minute"]
            datetime = f"{day}, {hour}:{minute}"
            return datetime
        else:
            print("Error:", response.status_code, response.text)

    def check_city_name(self, forecastOrActual: str) -> None:
        """
        on click of 'Weather' this method is called to check if the city_name input field has an entry and
        whether it calls the Weather Method or it opens Error Popup
        
        :param forecastOrActual: indicates which method needs to be called (current/forecast)
        in case the input field is not empty
        """
        city_name = self.root.get_screen('main').ids.city_name.text
        if city_name.strip() != "":
            if forecastOrActual == 'actual':
                self.current_weather_data(city_name)
            elif forecastOrActual == 'forecast':
                self.forecast_weather_data(city_name)
        else:
            # if response not okay, open popUp and open start screen again
            self.open_error_pop_up()

    def fetch_geodata(self, city: str):
        """
        gives a list back with latitude and longitude data
        of a given city and an flag value (0/1) to show wether the data
        come from the city.list.json.gz or from the geocoding API
        
        :param city: The name of the city the user searches for
        :return: a list object with geodata(lat and lon) and a flag value (0/1)
        """
        
        with gzip.open("/Users/sophieischenko/Downloads/city.list.json.gz", "rt") as f:
            expected_dict = json.load(f)

        lat = None
        lon = None
        city_geo = None


        for i in expected_dict:
            if i['name'] == city:
                lat = (i['coord']['lat'])
                lon = (i['coord']['lon'])
                city_geo = (i['name'])
                break
            
        if lat is not None and lon is not None and city_geo is not None:
            print(f"Found {city_geo} in expected_dict with latitude {lat} and longitude {lon}")
            return [lat, lon, 0]
        else:
            
            api_url_geodata = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_keys["openweather"]}'
            response_openweather = requests.get(api_url_geodata)
            data_geo = response_openweather.json()
            if response_openweather.status_code == requests.codes.ok:
                if len(data_geo) > 0:
                    lat = data_geo[0]["lat"]
                    lon = data_geo[0]["lon"]
                    city_geo = data_geo[0]["name"]
                    
                    return [lat, lon, 1]
                else:
                    self.open_error_pop_up()
            else:
                print("Error:", response_openweather.status_code,
                    response_openweather.text)

    def current_weather_data(self, city: str) -> None:
        """
        sets ui of the main window based on json data from openweather api
        
        :param city: The name of the city the user searches for
        """
        city_cap = city.capitalize()
        geodata = self.fetch_geodata(city_cap)
        
        if not geodata:
            return None
        
        lat = geodata[0]
        lon = geodata[1]
        city_found = geodata[2]

        api_url_openweather = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_keys["openweather"]}'
        response = requests.get(api_url_openweather)
        if response.status_code == 200:
            data_current = response.json()
            city_geo = data_current["name"]
            
            if city_found==1:
                self.alternative_city_pop_up(city_geo)
                
            country_geo = data_current["sys"]["country"]
            datetime = self.datetime(city)
            self.root.get_screen('main').ids.datetime.text = datetime
            pic_id = data_current["weather"][0]["id"]
            image_file = weather_images.get(pic_id, weather_images["default"])
            self.root.get_screen('main').ids.weather_image.source = image_file
            temperature = data_current["main"]["temp"]
            humidity = data_current["main"]["humidity"]
            self.root.get_screen('main').ids.temperature.text = f"{temperature}°"
            self.root.get_screen(
                'main').ids.humidity.text = f"humidity {humidity}%"
            pic_id = data_current["weather"][0]["id"]
            advice = weather_advice.get(pic_id, weather_advice["default"])
            self.root.get_screen('main').ids.advice.text = advice
            self.root.get_screen('main').ids.city.text = city_geo
            self.root.get_screen('main').ids.country.text = str(country_geo)
            windspeed = data_current["wind"]["speed"]
            self.root.get_screen('main').ids.windspeed.text = f"{windspeed} km/h"
            description = data_current["weather"][0]["description"]
            self.root.get_screen('main').ids.description.text = description
        else:
            print("Error:", response.status_code, response.text)

    # Everything on Forecast Window

    def forecast_weather_data(self, city: str) -> None:
        """
        sets ui of the forecast window based on json data from openweather api
        
        :param city: The name of the city the user searches for
        """
        city_cap = city.capitalize()
        geodata = self.fetch_geodata(city_cap)
        
        if not geodata:
            return None
        
        lat = geodata[0]
        lon = geodata[1]
        
        api_url_openweather = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&cnt=3&appid={api_keys["openweather"]}'
        response_openweather = requests.get(api_url_openweather)
        if response_openweather.status_code != requests.codes.ok:
            print("Error:", response_openweather.status_code,
                  response_openweather.text)
                
        data_forecast = response_openweather.json()
        self.root.get_screen('forecast').ids.forecastCity.text = data_forecast['city']['name']
        # get temperature, description, windspeed from data_forecast
        forecasts = data_forecast['list'][:3]
        for i, forecast in enumerate(forecasts):
            temperature = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            windspeed = forecast['wind']['speed']
            # set t, d, w on screen forecast
            self.root.get_screen('forecast').ids[f"temperatureForecast{i+1}"].text = f"{temperature}°"
            self.root.get_screen('forecast').ids[f"descriptionForecast{i+1}"].text = str(description)
            self.root.get_screen('forecast').ids[f"windspeedForecast{i+1}"].text = f"wind speed {windspeed} km/h"

     # All about the Pop-Up

    def open_error_pop_up(self):
        """
        method creates popUp window and calls it to open
        """
        # layout and position of the popUp
        layout = FloatLayout()

        popupLabel1 = Label(text="Either you didn't type in any city",
                            pos_hint={"center_x": 0.5, "center_y": 0.8})
        popupLabel2 = Label(text="nor the city wasn't found",
                            pos_hint={"center_x": 0.5, "center_y": 0.6})
        popupLabel3 = Label(text="check for spelling",
                            pos_hint={"center_x": 0.5, "center_y": 0.4})

        closeButton = Button(text="Close", size_hint=(0.8, 0.2),
                             pos_hint={"center_x": 0.5, "center_y": 0.1})

        layout.add_widget(popupLabel1)
        layout.add_widget(popupLabel2)
        layout.add_widget(popupLabel3)
        layout.add_widget(closeButton)

        # Instantiate popup and display
        popup = PopUpWindow(title='Something went wrong',
                                 content=layout,
                                 size_hint=(0.9, 0.5),
                                 pos_hint={"center_x": 0.5, "center_y": 0.5},
                                 )
        popup.open()

        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press=popup.dismiss)
        
    def alternative_city_pop_up(self, city: str):
        """
        method creates popUp window and calls it to open
        
        :param city: The name of the city the user searches for
        """
        
        layout=FloatLayout()
        popupLabel1 = Label(text="Your city wasn't found",
                            pos_hint={"center_x": 0.5, "center_y": 0.8})
        popupLabel2 = Label(text="Data is available froms",
                            pos_hint={"center_x": 0.5, "center_y": 0.6})
        popupLabel3 = Label(text= city,
                            pos_hint={"center_x": 0.5, "center_y": 0.4})

        closeButton = Button(text="Close", size_hint=(0.8, 0.2),
                             pos_hint={"center_x": 0.5, "center_y": 0.1})

        layout.add_widget(popupLabel1)
        layout.add_widget(popupLabel2)
        layout.add_widget(popupLabel3)
        layout.add_widget(closeButton)

        # Instantiate popup and display
        popup = PopUpWindow(title='Something went wrong',
                                 content=layout,
                                 size_hint=(0.9, 0.5),
                                 pos_hint={"center_x": 0.5, "center_y": 0.5},
                                 )
        popup.open()

        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press=popup.dismiss)
        

if __name__ == "__main__":
    showWeatherApp().run()
