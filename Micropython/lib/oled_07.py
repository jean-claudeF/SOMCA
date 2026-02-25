# oled_06_plus_test.py
# Began to write a class handling bigger fonts
# to continue, see:
# https://github.com/peterhinch/micropython-font-to-py/blob/master/writer/writer.py
# https://github.com/easytarget/microPyEZfonts?tab=readme-ov-file
# https://github.com/peterhinch/micropython-font-to-py
# https://github.com/easytarget/microPyEZfonts/tree/main/examples
# https://github.com/easytarget/microPyEZfonts/tree/main/drivers
# https://github.com/easytarget/microPyEZfonts/blob/main/WRITER.md

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

Big text (needs font16x16):
oled.text16("Some text", 5, 25)
oled.text16("Some text", 5, 25, xoffset = 12)     (xoffset decides spacing, 10...16)

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
# EXTENSION FOR BIG TEXT  16x16 needs font16x16.py
# Use Font16, otherwise print text in small font
USE_FONT16 = True

if USE_FONT16:
    try:
        from font16x16 import *
        from framebuf import FrameBuffer, MONO_HLSB
    except:
        USE_FONT16 = False
        




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
    # This is necessary as the OLED class must be based on either
    # _OLED(SH1106_I2C) or _OLED(SSD1306)
    # This must be assigned before creating the OLED class
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
        
        
        def draw_char16(self, ch, x, y):
            
            if ch not in font_16x16:    
                return  # Skip unknown characters
            bitmap = font_16x16[ch]
            b = bytearray(bitmap)
            fb = FrameBuffer(b, 16, 16, MONO_HLSB)
            self.blit(fb, x, y)  
        
        
        
        def text16(self, text, x, y, xoffset = 11):
            # xoffset = horizontal move to next charactr of text
            # use 10...16
            if USE_FONT16:
                for ch in text:
                    self.draw_char16(ch, x, y)
                    x += xoffset  # Move x to the right for the next character
            else:
                self.text(text, x, y)
                
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
#----------------------------------------------------------------


"""
framebuf.MONO_HLSB¶
    Monochrome (1-bit) color format This defines a mapping where the bits in a byte are horizontally mapped.
    Each byte occupies 8 horizontal pixels with bit 7 being the leftmost.
    Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached.
    Further bytes are rendered on the next row, one pixel lower.
"""


#----------------------------------------------------------



if __name__ == "__main__":
    from machine import Pin, I2C
    
    i2c = I2C(1, scl=Pin(19), sda=Pin(18))
    
    # Set the OLED type and create OLED class:
    set_oled_type("SSD1306")        # or set_oled_type("SH1106")
    
    OLED = create_oled_class()
    oled = OLED(128, 64, i2c, rotate=180)

    oled.text("Hello, World!", 2, 2)
    
    #oled.draw_char16('1', 0, 0)
    #oled.draw_char16('j', 0, 16)
    oled.text16("0123456789", 0, 16)
    oled.text16("abcdefghij", 0, 32)
    oled.text16("5.23V",0,48) 
    oled.rect(0,0,127,63,1)
    
    oled.show()
