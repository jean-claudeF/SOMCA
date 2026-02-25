
# Transformed values of ADC:
# v = adc.factors[i] * (v + adc.offsets[i])

from adc_ADS1115_04 import ADS1115
from machine import Pin, I2C
import time

btn_start = Pin(14, Pin.IN, Pin.PULL_UP)
btn_stop = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(16, Pin.OUT)


    
    

i2c_channel = 1
sclpin = 19
sdapin = 18
i2c = I2C(i2c_channel, scl=Pin(sclpin), sda=Pin(sdapin))
adc = ADS1115(i2c, address = 72, gain = 1)

# voltage:
adc.factors[0] = 20  #* 1.035298
adc.offsets[0] = 0.0006

# current:
adc.factors[1] = 10
adc.offsets[1] = 0.002

i = 0
while True:
    
    if btn_start.value() == 0:
        led.value(1)
        print("ON")
    if btn_stop.value() == 0:
        led.value(0)
        print("OFF")
    
    
    #v = adc.read(rate = 0, channel1 = 0)
    #v = adc.read_meanvalue(rate = 0, channel1 = 0, nb = 10)
    #v = adc.read_all_meanvalue(rate = 0, nb = 3)
    #v = adc.read(channel1 = 2, channel2 = 3) 
    
    #v = adc.read_all_as_string()
    if i % 10:    
        v = adc.read_all_as_string_meanvalue(nb = 10)
        print(v)
    
    time.sleep(0.1)
    i += 1