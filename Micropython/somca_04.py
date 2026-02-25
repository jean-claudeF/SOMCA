# SOMCA 04
# Switch off load and measure capacity

# Intervals in seconds for storing data in internal filesystem:
store_interval1 = 2       # beginning
store_interval2 = 60      # when longer than 1 minute
store_interval = 1        # initial value

current_min = 0.03        # current smaller than this is set to zero to avoid summing over nearly nothing thus causing errors in Q and W

filename = 'values.dat'
header = '# t/s \t U/V \t I/A \t Q/As \t Q/mAh \t P/W \t W/mWh\n'



from oled_07 import create_oled_class, set_oled_type
from machine import Pin, ADC, Timer, I2C, PWM, UART
import time
import os, sys

from adc_ADS1115_04 import ADS1115
from mcp23017_01 import MCP23017

# Interrupt timer:
timer = Timer()

#-----------------------------------------------------
# Hardware related:
# Buttons and LED = switch on / off:
btn_start = Pin(14, Pin.IN, Pin.PULL_UP)
btn_stop = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(16, Pin.OUT)
gate = Pin(17, Pin.OUT)

# I2C: OLED and ADC
i2c = I2C(1, scl=Pin(19), sda=Pin(18))
set_oled_type("SH1106")
OLED = create_oled_class()
oled = OLED(128, 64, i2c, rotate = 180)
oled.clear()

adc = ADS1115(i2c, address = 72, gain = 1)

# voltage lin. transform:
adc.factors[0] = 20  #* 1.035298
adc.offsets[0] = 0.0006

# current lin. transform:
adc.factors[1] = 10
adc.offsets[1] = 0.002

# Threshold voltage via BCD switches and port expander:
mcp = MCP23017(i2c)
mcp.reverse_A = True     # this gives the same bit sequence as for B (with A0 on pin 20)
mcp.init_BCD4()
##mcp.print_regs()

# extra UART (non USB):
uart = UART(0, baudrate = 9600)

"""
# DAC via PWM for current setting (if needed later):
pwm = PWM(Pin(3))
pwm.duty_u16(32767)
pwm.freq(100000)

def set_dac(v):
    duty = int(65535 * v / 3.3)
    pwm.duty_u16(duty)
"""

#--------------------------------------------------------------------
seconds = 0
voltage = 0
current = 0
nbval = 0

Q_As = 0
Q_mAh = 0
power = 0
energy_mWh = 0


#------------------------------------------------------
def get_threshold():
    # Read threshold value from BCD switches
    c = mcp.read_BCD4()
    return float(c)/100

#----------------------------------------------------

def say_hello():
    print("ACCU DISCHARGE")
    print("# I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
    print("# I2C Configuration: "+str(i2c))                   # Display I2C config
    print("# Waiting for start button")
    
    time.sleep(1)


def print_values():
    s = "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (seconds, voltage, current, Q_As, Q_mAh)
    print(s)
    uart.write(s + '\n\r')
    
    
def oled_waiting():
    oled.fill(0)
    #oled.text("%.3f V" % voltage, 0, 12)
    oled.text("WAIT for START",0,2)
    oled.text16("%.3f V" % voltage, 0, 20)
    oled.text("STOP = Send data", 0, 50)
    oled.show()

def oled_running():
    oled.fill(0)
    oled.text(str(seconds) +"s", 0, 0)
    oled.text("%.2f V" % voltage, 0, 12)
    oled.text("%.2f A" % current, 0, 24)
    oled.text("%i mAh" % Q_mAh, 0, 36)
    oled.text("RUNNING", 0, 48)
    oled.show()
    
def oled_stopped():
    oled.fill(0)
    oled.text(str(seconds) + "s", 0, 0)
    oled.text("%.2f V" % voltage, 0, 12)
    oled.text("%.2f A" % current, 0, 24)
    oled.text("%i mAh" % Q_mAh, 0, 36)
    oled.text("STOPPED", 0, 48)
    oled.show()

def oled_sentdata(l):
    oled.fill(0)
    oled.text("SENT DATA", 0, 12)
    oled.text(str(l) + " chars", 0, 24)
    oled.text("RESET TO START", 0, 48)
    oled.show()

def oled_error(e):
    oled.fill(0)
    oled.text("ERROR !", 0, 12)
    oled.text(e, 0, 24)
    oled.text("RESET TO START", 0, 48)
    oled.show()

"""
def set_current(I):
    # (if needed later)
    set_dac(I)
"""

#--------------------------------------------------------

def set_current(onoff):
    # for now, switch load on or off
    gate.value(onoff)


    
def measure():
    # measure and read threshold
    global voltage, current, threshold, Q_As, Q_mAh
    
    values = adc.read_all_meanvalue(rate = 4, nb = 10)
    voltage = values[0]
    current = values[1]
    if current < current_min:
        current = 0
    threshold = get_threshold()
    
    
    
#-------------------------------------------------------------
import gc
def print_free_memory():
    free_memory = gc.mem_free()
    print("Free memory: {} bytes".format(free_memory))
    
#------------------------------------------------------------------------
def delete_old_file():
    try:
        os.remove(filename)
        print("# Remove old " + filename)
    except:
        print("# Could not delete " + filename)
        print(os.listdir())


def create_file():
    try:
        f = open(filename, 'w')
        f.write('# Measure capacity\n')
        f.write("# V0 = %.3fV\n" % idle_voltage)
        f.write(header)       
        f.close()
    except:
        print("Error creating " + filename)

    
def store():
    s = "%i\t%.3f\t%.2f\t%.2f\t%.3f\t%.2f\t%.0f" % (seconds, voltage, current, Q_As, Q_mAh, power, energy_mWh)
    f = open(filename, "a") 
    f.write(s + '\n')
    f.close()    

def store_footer():
    f = open(filename, "a")
    f.write("# STOPPED at %.3fV\r\n" % voltage)
    f.write("# Q = %.2fmAh\r\n" % Q_mAh)
    f.write("# W = %.0fmWh\r\n" % energy_mWh)
    f.close()

def send_data():
    # Read data from internal filesystem file and transmit them via USB and UART
    # ( Not really needed if software on PC is used)
    led.on()
    ##time.sleep(1)
    print()
    try:
        f = open(filename, 'r')
        t = f.read()
        f.close()
        print(t)
        print()
        
        uart.write('\n\r\n')
        for l in t.splitlines():
            uart.write(l + '\r\n')
            time.sleep(0.01)
        uart.write('\n\r\n')
        oled_sentdata(len(t))
    except:
        print("Could not read " + filename)
        oled_error("Error sending data")
    ##time.sleep(1)
    led.off()
    
#----------------------------------------------------------

# These are the main loops:
    
def waiting_loop():
    # Wait for button start
    global idle_voltage
    while btn_start.value():
        if btn_stop.value() == 0:
            send_data()
            #sys.exit()
        measure()
        print("##   %.3fV" % voltage, end = '\r')
        #uart.write("##   %.3fV\r" % voltage)
        idle_voltage = voltage
        oled_waiting()
        time.sleep(0.05)
        
        if btn_start.value() == 0:
            gate.on()
            print("## ON")
            time.sleep(0.03)
            return

def measuring_loop():
    # Once the start button is pushed, measure in a loop
    # until either STOP button is pushed or voltage goes below threshold
    # Store values, in short intervals at the beginning and longer intervals
    # later, to avoid filesystem overflow
    
    global seconds, voltage, current, threshold, Q_As, Q_mAh, power, energy_mWh
    
    time0 = time.time()        # start time of loop
    time1 = time0              # effective cycle time
    time_store = time0
    
    measure()
    
    
    Q_As = 0
    Q_mAh = 0
    energy_mWh = 0
    energy_Ws = 0
    
    i = 0
    while True:
        
        # print header every 10 lines:
        if i % 10 == 0:
            print(header)
            uart.write(header + '\r\n')
            i+=1
        
        # Stop if STOP btn or < threshold:    
        if btn_stop.value() == 0  or voltage < threshold:
            gate.off()
            print("## OFF")
            time.sleep(0.03)
            return
        
        # every second:
        if time.time()-time1 >= 1:
            time1 = time.time()
            seconds = time.time()-time0
                        
            led.on()
            measure()
            power = voltage * current
            Q_As += current
            Q_mAh = Q_As / 3.6
            energy_Ws +=  power
            energy_mWh = energy_Ws / 3.6
            
            s = s = "%i\t%.3f\t%.3f\t%.2f\t%.2f\t%.1f\t%.0f" % (seconds, voltage, current, Q_As, Q_mAh, power, energy_mWh)
            print(s)
            uart.write(s + '\r\n')
            oled_running()
            led.off()
            
            
        
        
            # store every store_interval
            if seconds <= 60:
                store_interval = store_interval1
            else:
                store_interval = store_interval2
            
            if time.time()-time_store >= store_interval:
                time_store = time.time()
                print("# Storing")
                store()
        
        time.sleep(0.01)
        
def print_footer():
    # Print important data at the bottom
    
    print("# STOPPED at %.3fV" % voltage)
    print("# Q = %.2fmAh" % Q_mAh)
    print("# W = %.0fmWh" % energy_mWh)
    
    uart.write("# STOPPED at %.3fV\r\n" % voltage)
    uart.write("# Q = %.2fmAh\r\n" % Q_mAh)
    uart.write("# W = %.0fmWh\r\n" % energy_mWh)


    
#--------------------------------------------------------------------------------------
##   MAIN
threshold = get_threshold()

print_free_memory()

while True:

    set_current(0)
    say_hello()
    
    waiting_loop()
    
    # Prepare things:
    print("\n # Start")
    print(header)
    delete_old_file()
    measure()
    create_file()
    
    # Switch on and measure until stopped
    # by button or undervoltage:
    set_current(1)
    store()
    measuring_loop()
        
    # When stopped:    
    set_current(0)
    print_footer()
    store_footer()
    oled_stopped()
    
    time.sleep(1)
    
    # Restart? Wait for start button
    print("RESTART -> START")
    time.sleep(1)
    
    while btn_start.value():
        time.sleep(0.05)
        
