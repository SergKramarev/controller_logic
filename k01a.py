from machine import Pin, I2C, Timer, reset
from time import sleep
import gc

from pcf8574 import PCF8574
from esp8266_i2c_lcd import I2cLcd

import ssd1306

# инициализируем голубой светодиод на модуле контроллера
led = Pin(2,Pin.OUT,value=1)


# Инициализируем шину I2C
bus = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
# Ищем все подключенные к линии физические устройства (микросхемы расширения)
devices = bus.scan()

# Отображение найденных устройств
print(devices)

# Создаем свой класс для глобальных состояний
class globalstate:
    def __init__(self,set_value:int):
        self.value = set_value
    def set(self,set_value:int):
        self.value = set_value

temperature = globalstate(0)
humidity = globalstate(0)
brightness = globalstate(0)

alarm = globalstate(0)


# Проверка наличия на шине необходимых интерфейсов
try:
    relays = PCF8574(i2c=bus, address=32) # релейные выходы контроллера (лампы, подогрев, увлажнитель)
    inputs = PCF8574(i2c=bus, address=62) # цифровые входы контроллера (кнопки и дискретные датчики)

except:
    alarm.set(1)


# Проверка наличия на шине экранчика
if 60 in devices:
    oled = ssd1306.SSD1306_I2C(128, 32, bus, 60)


# сбор мусора для очистки памяти
gc.collect()


def operate(arg):
    # замер освещенности с сохранением в глобальную переменную
    # замер температуры с сохранением в глобальную переменную
    # замер влажности с сохранением в глобальную переменную

    # логика и выполнение действий, например:
    if brightness.value < 500:
        relays.write(0,1)
        relays.write(1,1)
        relays.write(2,1)
    elif brightness.value < 2000:
        relays.write(0,1)
        relays.write(1,1)
        relays.write(2,0)
    elif brightness.value < 5000:
        relays.write(0,1)
        relays.write(1,0)
        relays.write(2,0)
    else:
        relays.write(0,0)
        relays.write(1,0)
        relays.write(2,0)

    # вызовы вспомогательных функций
    show()
    save_db()


# Функция отображения информации на экране
def show():
    if 60 in devices:
        oled.fill(0) #стираем экран
        oled.text(str(brightness.value) + "lux", 0, 0) #задание на отображение текста в первой строке
        oled.text(str(temperature.value) + "degrees", 0, 11) #задание на отображение текста во второй строке (смещение по оси x=0, по оси y=-11)
        oled.text(str(humidity.value) + "%", 0, 22) #задание на отображение текста в третьей строке (смещение по оси x=0, по оси y=-22)
        oled.show()

def save_db():
    with open("db.csv", 'a') as sv_file:
        sv_file.write(str(brightness.value)+';'+str(temperature.value)+'\r'+str(humidity.value)+'\r')


# отключаем динамик и одновременно с этим включаем разрешающий пин (свидетельсвто успешной загрузки данного скрипта)
buzzer = Pin(16,Pin.OUT,value=0)

tim = Timer(-1)
# Инициируем таймер на постоянное срабатываение через каждые 1000 мс (1 секунда) с вызовом ранее созданной функции
tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:operate(1))