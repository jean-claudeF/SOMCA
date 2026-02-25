''' Test for oled_06.py
Is for:
SH1106     The big one 1.3"       +Vcc left!
SSD1306    The small one 0.96"    GND left!

To change type use this:
set_oled_type("SH1106")   or  set_oled_type("SSD1306") 
'''

from machine import Pin, I2C
import time
from oled_06 import create_oled_class, set_oled_type

i2c = I2C(1, scl=Pin(19), sda=Pin(18))
#set_oled_type("SSD1306")
set_oled_type("SH1106")
OLED = create_oled_class()
oled = OLED(128, 64, i2c, rotate = 180)
oled.clear()

def test1():
    oled.clear()
    oled.print("TEST OLED PRINT")
    for i in range(0,8):
        #oled.print_line("TEST " + str(i))
        oled.print("TEST " + str(i))
        time.sleep(0.2)
        oled.show()

def test2():
    oled.clear()

    oled.text("TEST OLED", 0, 0)      # text, x, y, colour (1 = white)     
    #oled.text("TEST OLED",5,5)
    oled.text("by JCF",5,15)
    oled.text("Another row", 5, 25)
    oled.text("Yet another row", 5, 35)
    oled.text("And one more", 5, 45)
    oled.show()



def test3():
    oled.clear()
    oled.text("TEST ", 30, 0)             
    oled.hline(10,10, 20, 1)
    oled.vline(10, 20, 30, 1)
    oled.line(10, 10, 50, 50, 1)
    oled.rect(20, 20, 60, 40, 1)
    oled.fill_rect(80, 20, 20, 20, 1)
    oled.show()



def test4():
    oled.clear()
    for i in range(0,6):
        #oled.print_line("TEST LINE" + str(i))
        oled.print("TEST LINE" + str(i))
    oled.show()               

def test5():
    s = "Hello \t world \t ! \t 3.14     \t The answer is \t 42"
    oled.print_s(s)
    '''
    time.sleep(1)
    s = "123456789 \t ! \t 3.14     \t The answer is \t 42\t Hitchhiker"
    oled.print_s(s) 
    '''
def test6():
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    oled.clear()
    '''
    sc = compact_string(s, 16)
    oled.print(sc)
    '''
    oled.print_compact(s)
    
    
def test_all():
    test1()
    time.sleep(1)
    test2()
    time.sleep(1)
    test3()
    time.sleep(1)
    test4()
    time.sleep(1)
    test5()
    time.sleep(1)
    test6()
    
    

test_all()
