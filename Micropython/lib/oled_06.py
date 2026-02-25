# oled_06.py
# For SH1106 / SSD1306
# Needs sh1106.py or ssd1306.py  drivers (Import is automatically done by create_oled_class())
'''
USE LIKE THIS:
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
    
# Set the OLED type and create OLED class:
set_oled_type("SSD1306")        # or set_oled_type("SH1106")
OLED = create_oled_class()
oled = OLED(128, 64, i2c, rotate=180)
oled.clear()

Text:
oled.print("TEST OLED PRINT")
oled.text("Some text", 5, 25)
oled.print_s("Hello \t world \t The answer is \t 42")      (\t defines new line here!)

Compact text that is too long for display:
s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
oled.print_compact(s)

Graphics provided by framebuffer (no extras required):
oled.hline(10,10, 20, 1)
oled.vline(10, 20, 30, 1)
oled.line(10, 10, 50, 50, 1)
oled.rect(20, 20, 60, 40, 1)
oled.fill_rect(80, 20, 20, 20, 1)

oled.show()    must be called to display
'''
#--------------------------------------------
# Global variable to hold the OLED type
OLED_TYPE = None

def set_oled_type(oled_type):
    # set type SH1106 / SSD1306
    # this must be done first!
    global OLED_TYPE
    OLED_TYPE = oled_type

def _prepare_oled_class():
    # Import the correct driver and prepare _OLED class
    # depending on type SH1106 / SSD1306
    global OLED_TYPE
    if OLED_TYPE is None:
        raise ValueError("OLED_TYPE is not set. Please call set_oled_type() first.")
    
    if OLED_TYPE == "SH1106":
        from sh1106 import SH1106_I2C as OLED_Driver
    elif OLED_TYPE == "SSD1306":
        from ssd1306 import SSD1306_I2C as OLED_Driver
    else:
        raise ValueError("Invalid OLED_TYPE. Expected 'SH1106' or 'SSD1306'.")
    
    class _OLED(OLED_Driver):
        def __init__(self, width, height, i2c, res=None, addr=0x3c,
                     rotate=0):
            # init base class:
            if OLED_TYPE == "SH1106":
                super().__init__(width, height, i2c,  addr=addr, rotate=rotate)
            else:
                super().__init__(width, height, i2c,  addr=addr)
                
    return _OLED

def create_oled_class():
    # create OLED class inheriting from _OLED class
    # this can then be used as usual: oled = OLED(128, 64, i2c)
    _OLED = _prepare_oled_class()
    
    class OLED(_OLED):
        def __init__(self, width, height, i2c, res=None, addr=0x3c,
                     rotate=0):
            self.currentline = 0
            self.maxline = 5
            
            self.i2c = i2c
            self.addr = addr
            self.res = res
            
            # init base class:
            if OLED_TYPE == "SH1106":
                super().__init__(width, height, i2c,  addr=addr,
                             rotate=rotate)
            else:
                super().__init__(width, height, i2c,  addr=addr)
                             
            # Additional methods or properties can be added here
        def clear(self):
            self.fill(0)
            self.currentline = 0
    
        
                    
        def write_line(self, text, line):
            '''write text to OLED into line 0...5'''
            self.text(text, 0, line * 10)
            self.show()


        def print(self, text):
            '''print string s to OLED and automatically go to next row
               with clear before line 0'''
            if self.currentline == 0:
                self.fill(0)
            self.write_line(text,  self.currentline )
            self.currentline += 1
            if self.currentline > self.maxline:
                self.currentline = 0
        
        
            
        def print_s(self, s, separator = '\t'):
            '''print string s to OLED
            s -> multiple rows, separated by '\t'   '''
            
            sarray = s.split(separator)
            self.fill(0)
            self.currentline = 0
            for item in sarray:
                #self.print(item)
                self.text(item, 0, self.currentline * 10)
                self.currentline += 1
                if self.currentline > self.maxline:
                    self.currentline = 0
            self.show()    

        def print_compact(self, s, nbchars = 16):
            '''print strings that are too long by cutting out the mid section'''
            sc = compact_string(s, nbchars)
            self.print(sc)
            
    return OLED

def compact_string(s, nbchars):
    # return first characters and end of a string
    # for OLED displays that cannot display the whole string
    sl = s[:3] + ".."
    l_left = len(sl)
    l_right = nbchars - l_left
    midpos = len(s) - l_right
    sr = s[midpos :]
    sn =  sl + sr
    return sn

#----------------------------------------------------------
if __name__ == "__main__":
    from machine import Pin, I2C
    
    i2c = I2C(0, scl=Pin(9), sda=Pin(8))
    
    # Set the OLED type and create OLED class:
    set_oled_type("SSD1306")        # or set_oled_type("SH1106")
    OLED = create_oled_class()
    oled = OLED(128, 64, i2c, rotate=180)

    oled.text("Hello, World!", 0, 0)
    oled.show()
