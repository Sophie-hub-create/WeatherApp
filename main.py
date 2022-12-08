import requests
import arrow
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen

class WindowManager(ScreenManager):
    pass

class ForecastWindow(Screen):
    pass

class ErrorPopUpWindow(Popup):
    pass

class MainWindow(Screen):
    pass

class showWeatherApp(App):
    
    def build(self):
        Window.clearcolor=(0.94 ,0.87, 0.706,1)
        
    # Everything on Main Window (current weather)
    
    def on_start(self):
        """method ensures how screen looks like on start"""
        self.root.get_screen('main').ids.country.text='DE'
        self.root.get_screen('main').ids.city.text='Berlin'
        self.get_current_weather('Berlin')
        self.get_forecast_weather('Berlin')
        #self.root.get_screen('main').ids.forecast.disabled=True
        
        
    def datetime(self, city):
        """method for setting Weekday and time of a given city"""
        api_url = 'https://api.api-ninjas.com/v1/worldtime?city={}'.format(city)
        response = requests.get(api_url, headers={'X-Api-Key': })
        datetime_data=response.json()
        if response.status_code == requests.codes.ok:
            # get day, hour, minute from data und format (Monday, 12:05) 
            day = datetime_data["day_of_week"]
            hour = datetime_data["hour"]
            minute = datetime_data["minute"]
            datetime= day + ", "+hour+":"+minute
            return datetime
        else:
            # if response not okay, open popUp and open start screen again
            self.open_pop_up()
            self.on_start()
            print("Error:", response.status_code, response.text)
    
    def current_weather(self):
        """on click of 'Show Weather' this method is called to check if the city_name input field has an entry and
        whether it calls the Weather Method or it opens Error Popup"""
        city_name=self.root.get_screen('main').ids.city_name.text
        if city_name !="Enter city":
            self.get_current_weather(city_name)
        else:
            # if response not okay, open popUp and open start screen again
            self.open_pop_up() 
            self.on_start()

    def get_geodata(self, city):
        """gives an arry back with latitude and longitude data of a given city"""
        #global array_geodata 
        array_geodata=[]
        api_url_geodata='http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=.format(city=city)
        response_openweather = requests.get(api_url_geodata)
        data_geo = response_openweather.json()
        if response_openweather.status_code == requests.codes.ok:
            try:
                lat = data_geo[0]["lat"]
                lon=data_geo[0]["lon"]
                city_geo= data_geo[0]['name']
                country_geo= data_geo[0]['country']
                array_geodata.append(lat)
                array_geodata.append(lon)
                array_geodata.append(city_geo)
                array_geodata.append(country_geo)
                #self.root.get_screen('main').ids.city.text=city_geo
                return array_geodata
            except:
                # if an error occurs (user input), open popUp and open start screen again
                self.open_pop_up()
                self.on_start()
        else:
            print("Error:", response_openweather.status_code, response_openweather.text)
    
    def get_current_weather(self, city):
        """method stores data from get_geodata method and calls weather data method with these parameters"""
        try:
            geodata = self.get_geodata(city)
            lat = geodata[0]
            lon = geodata[1]
            city_geo=geodata[2]
            country_geo=geodata[3]
            self.get_current_weather_data(lat,lon, city_geo, country_geo) 
        except:
            # if an error occurs (user input), open popUp and open start screen again
            self.open_pop_up()
            self.on_start()
    
    def get_current_weather_data(self, lat, lon, city, country):
        """gives back json data for current weather based on latitude(float) + longitude(float) data"""
        api_url_openweather ='https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid=.format(lat=lat, lon=lon)
        response_openweather = requests.get(api_url_openweather)
        data_current = response_openweather.json()
        if response_openweather.status_code == requests.codes.ok:
            
            #try:
                print(response_openweather.text)
                # get pic id, temperature, humditiy, descriptipn, windspeed from data
                pic_id = data_current["weather"][0]["id"]
                temperature=data_current["main"]["temp"]
                humidity=data_current["main"]["humidity"]
                description=data_current["weather"][0]["description"]
                windspeed=data_current["wind"]["speed"]
                # set p, t, h, d, w on main window
                self.root.get_screen('main').ids.city.text=country
                self.root.get_screen('main').ids.city.text=city
                self.root.get_screen('main').ids.country.text = str(country)
                self.root.get_screen('main').ids.temperature.text= f"{temperature}°"
                self.root.get_screen('main').ids.humidity.text=f"humidity {humidity}%"
                self.root.get_screen('main').ids.description.text=str(description)
                self.root.get_screen('main').ids.windspeed.text= f"wind speed {windspeed} km/h" 
                if pic_id > 801:
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/cloudy.png"
                elif pic_id == 801: 
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/sunnycloudy.png"
                elif pic_id == 800: 
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/sun.png"
                elif pic_id < 700 and pic_id > 599: 
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/snow.png"
                    self.root.get_screen('main').ids.advice.text="Don't forget your gloves"
                elif pic_id < 532 and pic_id > 504: 
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/rainy.png"
                    self.root.get_screen('main').ids.advice.text="Don't forget your umbrella"
                elif pic_id <= 504 and pic_id > 321: 
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/sunnyrainy.png"
                    self.root.get_screen('main').ids.advice.text="Don't forget your umbrella"
                elif pic_id < 200 and pic_id > 99: 
                    self.root.get_screen('main').ids.weather_image.source="pics_weather/gewitter.png"
                    self.root.get_screen('main').ids.advice.text="Take care of yourself"
                datetime= self.datetime(city)
                self.root.get_screen('main').ids.datetime.text=datetime
                
            #except:
                # self.open_pop_up()
                # self.on_start()
        else:
            print("Error:", response_openweather.status_code, response_openweather.text)
                   
    # All about the Pop-Up   
         
    def open_pop_up(self):
        """method creates popUp window and calls it to open"""
        # layout and position of the popUp
        layout = FloatLayout()
  
        popupLabel = Label(text = "Either you didn't type in any city\n\nor the city wasn't found\n\n(check for spelling)",
                                pos_hint={"center_x":0.5, "center_y":0.6})
        closeButton = Button(text = "Close",size_hint=(0.8, 0.15),
                      pos_hint={"center_x":0.5, "center_y":0.1})
  
        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)       
  
        # Instantiate popup and display
        popup = ErrorPopUpWindow(title ='Something went wrong',
                      content = layout,
                      size_hint=(0.9, 0.5),
                      pos_hint={"center_x":0.5, "center_y":0.5},
                      )  
        popup.open()   
  
        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press = popup.dismiss)
        
    # Everything on Forecast Window
    
    def forecast_weather(self):
        """on click of 'Show Weather' this method is called to check if the city_name input field has an entry and
        whether it calls the Weather Method or it opens Error Popup"""
        city_name=self.root.get_screen('main').ids.city_name.text
        if city_name !="Enter city":
            self.get_forecast_weather(city_name)
        else:
            # if user input is empty, open PopUp and open start screen again
            self.open_pop_up() 
            self.on_start()
        
            
    def get_forecast_weather(self, city):
        """method stores data from get_geodata method and calls weather data method with these parameters"""
        #global array_geodata
        try:
            array_geodata = self.get_geodata(city)
            lat = array_geodata[0]
            lon = array_geodata[1]
            city_geo = array_geodata[2]
            self.get_forecast_weather_data(lat,lon, city_geo)
        except:
            # if an error occurs (user input), open popUp and open start screen again
            self.open_pop_up()
            self.on_start()
        
    def get_forecast_weather_data(self, lat, lon, city):
        api_url_openweather = 'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&cnt=3&appid=.format(lat=lat, lon=lon, cnt=3)
        response_openweather = requests.get(api_url_openweather)
        data_forecast = response_openweather.json()
        if response_openweather.status_code == requests.codes.ok:
            #try:
                print(response_openweather.text)
                # get days over arrow function/BIB
                now = arrow.now()
                tomorrow = now.shift(days=1)
                dayAfterTomorrow = now.shift(days=2)
                inThreeDays = now.shift(days=3)
                self.root.get_screen('forecast').ids.dayone.text=tomorrow.humanize()
                self.root.get_screen('forecast').ids.daytwo.text=dayAfterTomorrow.humanize()
                self.root.get_screen('forecast').ids.daythree.text=inThreeDays.humanize()
                self.root.get_screen('forecast').ids.forecastCity.text=city
                # get temperature, description, windspeed from data_forecast
                temperatureForecastOne = data_forecast['list'][0]['main']['temp']
                temperatureForecastTwo = data_forecast['list'][1]['main']['temp']
                temperatureForecastThree = data_forecast['list'][2]['main']['temp']
                descriptionForecastOne= data_forecast['list'][0]['weather'][0]['description']
                descriptionForecastTwo= data_forecast['list'][1]['weather'][0]['description']
                descriptionForecastThree= data_forecast['list'][2]['weather'][0]['description']
                windspeedForecastOne= data_forecast['list'][0]['wind']['speed']
                windspeedForecastTwo= data_forecast['list'][1]['wind']['speed']
                windspeedForecastThree= data_forecast['list'][2]['wind']['speed']
                # set t, d, w on screen forecast
                self.root.get_screen('forecast').ids.temperatureForecastOne.text=f"{temperatureForecastOne}°"
                self.root.get_screen('forecast').ids.temperatureForecastTwo.text=f"{temperatureForecastTwo}°"
                self.root.get_screen('forecast').ids.temperatureForecastThree.text=f"{temperatureForecastThree}°"
                self.root.get_screen('forecast').ids.descriptionForecastOne.text=str(descriptionForecastOne)
                self.root.get_screen('forecast').ids.descriptionForecastTwo.text=str(descriptionForecastTwo)
                self.root.get_screen('forecast').ids.descriptionForecastThree.text=str(descriptionForecastThree)
                self.root.get_screen('forecast').ids.windspeedForecastOne.text= f"wind speed {windspeedForecastOne} km/h" 
                self.root.get_screen('forecast').ids.windspeedForecastTwo.text= f"wind speed {windspeedForecastTwo} km/h" 
                self.root.get_screen('forecast').ids.windspeedForecastThree.text= f"wind speed {windspeedForecastThree} km/h"
                #self.root.get_screen('main').ids.forecast.disabled = True 
            # except:
            #     self.open_pop_up()
            #     self.on_start()
        else:
            print("Error:", response_openweather.status_code, response_openweather.text)
            
        
if __name__=="__main__":
    showWeatherApp().run()