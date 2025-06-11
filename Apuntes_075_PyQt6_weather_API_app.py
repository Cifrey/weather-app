import sys
import os
import requests
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QPainter, QPixmap, QIcon
from PyQt6.QtSvgWidgets import QSvgWidget

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_widget = QSvgWidget(self)
        self.emoji_widget.setFixedSize(QSize(150, 150))
        self.description_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setWindowIcon(QIcon("Python/weather_app/weathericon.png"))

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.emoji_widget)
        hbox.addStretch()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addLayout(hbox)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)
        
        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.city_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setObjectName("main_window")
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_widget.setObjectName("emoji_widget")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QPushButton{
                background-color: rgba(48, 48, 48, 150);            
            }               
            QLabel, QPushButton{
                font-family: Japanese Brush;               
            }
            QLabel#city_label{
                font-size: 40px;               
            }
            QLineEdit#city_input{
                font-size: 40px;
                font-family: Japanese Brush;
                color: white;
                background: rgba(48, 48, 48, 150);
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton#get_weather_button{
                font-size: 30px;
            }    
            QLabel#temperature_label{
                font-size: 75px;
                color: white;
                font-family: Hetigon Vintage;
            } 
            QLabel#description_label{
                font-size: 50px;
                color: white;
            }                                     
        """)

        self.get_weather_button.clicked.connect(self.get_weather)

    def paintEvent(self, event): # type: ignore
        painter = QPainter(self)
        pixmap = QPixmap("Python/weather_app/fondito5.png")
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2

        painter.drawPixmap(x, y, scaled_pixmap)

    def get_weather(self):
        
        load_dotenv()
        api_key = os.getenv("OPENWEATHER_API_KEY")
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)   

        except requests.exceptions.HTTPError as http_error:
            match response.status_code: # type: ignore
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease try again later")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout:\nNo response from the server")
                case _:
                    self.display_error("HTTP Error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your Internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_widget.load(QByteArray())
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_kelvin = data["main"]["temp"]
        temperature_celsius = temperature_kelvin - 273.15
        temperature_fahrenheit = (temperature_kelvin * 9/5) - 459.67
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.temperature_label.setText(f"{temperature_celsius:.0f}°C")
        self.set_weather_icon(weather_id)
        self.description_label.setText(weather_description.capitalize())
        self.city_input.clear()

    def set_weather_icon(self, weather_id):
        ICON_PATH = "Python/weather_app/"

        if 200 <= weather_id <= 232:
            icon_path = ICON_PATH + "thunderstorms-day-overcast-rain.svg"
        elif 300 <= weather_id <= 321:
            icon_path = ICON_PATH + "drizzle.svg"
        elif 500 <= weather_id <= 531:
            icon_path = ICON_PATH + "rain.svg"
        elif 600 <= weather_id <= 622:
            icon_path = ICON_PATH + "snow.svg"
        elif 701 <= weather_id <= 781:
            icon_path = ICON_PATH + "mist.svg"
        elif weather_id == 762:
            icon_path = ICON_PATH + "extreme-smoke.svg"
        elif weather_id == 771:
            icon_path = ICON_PATH + "wind.svg"
        elif weather_id == 781:
            icon_path = ICON_PATH + "tornado.svg"
        elif weather_id == 800:
            icon_path = ICON_PATH + "clear-day.svg"
        elif 801 <= weather_id <= 804:
            icon_path = ICON_PATH + "cloudy.svg"
        
        if icon_path: #type: ignore
            self.emoji_widget.load(icon_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec())