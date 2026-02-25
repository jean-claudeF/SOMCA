
from machine import Pin
import time


btn_start = Pin(14, Pin.IN, Pin.PULL_UP)
btn_stop = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(16, Pin.OUT)

while True:
    if btn_start.value() == 0:
        led.value(1)
        print("ON")
    if btn_stop.value() == 0:
        led.value(0)
        print("OFF")
    time.sleep(0.1)
    
