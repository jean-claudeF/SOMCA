# Switch off a load when voltage below value adjusted with BCD switches
#  MCP23017 reading 4 BCD switches in negative logic
# with interrupt for main program when a change occurs

from mcp23017_01 import MCP23017
from machine import Pin, I2C
import time

signal_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Example: GPIO15, pull-up resistor enabled


SDA = 18
SCL = 19

# Scan addresses
print("External devices on I2C port 1, GPIO%i (SCL), GPIO%i (SDA):" % (SCL, SDA))
i2c = I2C(1, scl=Pin(SCL), sda=Pin(SDA), freq=100000)
addresses = i2c.scan()
for a in addresses:
    print(hex(a))


def handle_interrupt(pin):
    
    mcp.int_clear()
    time.sleep(0.02)
    c = mcp.read_BCD4()
    print(c, end = '\r')
    #print("Interrupt triggered! Signal detected on pin:", pin)



mcp = MCP23017(i2c)
mcp.reverse_A = True     # this gives the same bit sequence as for B (with A0 on pin 20)

signal_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)


mcp.init_BCD4()
mcp.print_regs()


print("Reading 4 digit BCD")

# Initial value
c = mcp.read_BCD4()
print(c)

# Future values handled by interrupt
while True:
    # Do nothing or whatever you like...
    # Change handled by interrupt
    #c = mcp.read_BCD4()
    #print(c)
    time.sleep(0.5)
