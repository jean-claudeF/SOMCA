from adc_ADS1115_04 import ADS1115
from machine import Pin, I2C
import time


i2c_channel = 1
sclpin = 19
sdapin = 18
i2c = I2C(i2c_channel, scl=Pin(sclpin), sda=Pin(sdapin))
adc = ADS1115(i2c, address = 72, gain = 1)
adc.factors[0] = 20  #* 1.035298
adc.offsets[0] = 0.0006
while True:
    
    #v = adc.read(rate = 0, channel1 = 0)
    #v = adc.read_meanvalue(rate = 0, channel1 = 0, nb = 10)
    #v = adc.read_all_meanvalue(rate = 0, nb = 3)
    #v = adc.read(channel1 = 2, channel2 = 3) 
    
    #v = adc.read_all_as_string()
    v = adc.read_all_as_string_meanvalue(nb = 10)
    print(v)
    time.sleep(1)
