# Test MCP23017 as input port expander
# connected to I2C1
# After powerup, IOCON.BANK = 0


#----------------------------------------------
def reverse_bits(n):
    # reverse bits of an 8 bit integer
    n = ((n & 0xF0) >> 4) | ((n & 0x0F) << 4)  # Swap nibbles
    n = ((n & 0xCC) >> 2) | ((n & 0x33) << 2)  # Swap pairs of bits
    n = ((n & 0xAA) >> 1) | ((n & 0x55) << 1)  # Swap individual bits
    return n

# Rudimentary class for the port expander
class MCP23017():

    def __init__(self, i2c, mcp_addr=0x20):
        self.addr = mcp_addr
        self.i2c = i2c
        self.reverse_A = False    # reverse bits 0...7 -> 7...0
        self.reverse_B = False
        
    def read_regs(self):
        # read all 22 registers and return list of values
        x = self.i2c.readfrom_mem(self.addr, 0, 22)
        x = list(x)
        return x
    
    def write_reg(self, reg_addr, value):
        # write value into reg_addr 
        self.i2c.writeto_mem(self.addr, reg_addr,  bytes([value]))
    
    def pullup_all(self):
        # Set pullups 100k for A and B port
        self.write_reg(0xc, 0xFF)
        self.write_reg(0xd, 0xFF)

    def read_A(self):
        # Read 8 bits on port A
        x = self.i2c.readfrom_mem(self.addr, 0x12 , 1)
        x = x[0]
        if self.reverse_A:
            x = reverse_bits(x)
        return x
    
    def read_B(self):
        # Read 8 bits on port B
        x = self.i2c.readfrom_mem(self.addr, 0x13 , 1)
        x = x[0]
        if self.reverse_B:
            x = reverse_bits(x)
        return x

    def readinv_A(self):
        # Read 8 bits on A in negative logic
        x = self.read_A()
        return ~x & 0xFF
    
    def readinv_B(self):
        # Read 8 bits on B in negative logic
        x = self.read_B()
        return ~x & 0xFF

    def readinv_BCD_B(self):
        # Read value coded by 2 BCD encoders aon B
        # Common connected to GND
        x = self.readinv_B()
        x0 = x & 0xF
        x1 = (x & 0xF0) >> 4
        x = x0 + 10 * x1
        return x
    
    def readinv_BCD_A(self):
        # Read value coded by 2 BCD encoders aon B
        # Common connected to GND
        x = self.readinv_A()
        x0 = x & 0xF
        x1 = (x & 0xF0) >> 4
        x = x0 + 10 * x1
        return x
    
    def enable_int_A(self):
        self.write_reg(0x04, 0xFF) 

    def enable_int_B(self):
        self.write_reg(0x05, 0xFF)
        
    def mirror_int(self):
        # activate both interrupts A & B when A or B has changed
        self.write_reg(0x0A, 64)
    
    def int_clear(self):
        # read interrupt flag register to clear interrupt flag          ##TODO
        x = self.i2c.readfrom_mem(self.addr, 0x8, 1)
        

    def read_BCD4(self):
        # read 4 digit number with negative logic, B=MSD, A = LSD
        a = self.readinv_BCD_A()
        b = self.readinv_BCD_B()
        c = 100*b + a
        return c

    def init_BCD4(self):
        # init 4xBCD with neg. logic, enable + mirror interrupts
        self.pullup_all()
        self.enable_int_A()
        self.enable_int_B()
        self.mirror_int()
        
    def print_regs(self):
        print("Register values:") 
        x = self.read_regs()
        for i, r in enumerate(x):
            print(i, ":", r)
        print()
#-------------------------------------------------------
# TEST
if __name__ == "__main__":

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

    #if __name__ == "__main__":

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


