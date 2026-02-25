"""    SOMCA
       Get data and plot V = f(t)
       # t/s 	 U/V 	 I/A 	 Q/As 	 Q/mAh 	 P/W 	 W/mWh
       #  0       1       2       3        4      5        6

"""       

filename = "values.dat"
filename_save = "saved_values.dat"
folder = "data"

import time
from picoconnect_pa02 import *
import numpy as np
import matplotlib.pyplot as plt

from text_to_plot_01 import text2xy
from filetools_01 import Filetools



#---------------------------------------------------------------------

def plot_all(text, comment):
    
    t, v = text2xy(text, 0, 1)
    t = t / 3600
    v,  q = text2xy(text, 1, 4)
    q = q/1000
    _, w_mWh = text2xy(text, 0, 6) 
    w_Wh = w_mWh/1000
    
    tmax = max(t)
    qmax = max(q)
    wmax = max(w_Wh)
    vmin = min(v)
    vmax = max(v)
    duration = max(t)
    td = time.strftime("Time: %X %A %d.%m.%Y")
    qq = qmax - q
    ww = wmax - w_Wh
    
    print("duration = %.2f h"  % tmax)
    print("Min. voltage = %.2f V"  % vmin)
    print("Max. voltage = %.2f Ah"  % vmax)
    print("Max. charge = %.2f Ah"  % qmax)
    print("Max. energy = %.0f Wh"  % wmax)
    print(td)
    
    fig1 = plt.figure(figsize=(20, 20))     # in inches
    fig1.canvas.manager.set_window_title(comment + td )
    
    ax1 = fig1.add_subplot(221)
    l1, = ax1.plot (t, v)
    plt.title('v = f(t)')
    plt.ylabel("voltage / V")
    plt.xlabel("time / hours")
    plt.grid(True)

    ax2 = fig1.add_subplot(222)
    l2, = ax2.plot (v, q)
    plt.title('Q = f(V)')
    plt.ylabel('Charge to load/ Ah')
    plt.xlabel('Remaining voltage / V')
    plt.grid(True)
    
    ax3 = fig1.add_subplot(223)
    l3, = ax3.plot (v, qq)
    plt.title('voltage - charge dependency')
    plt.ylabel('Battery charge/ Ah')
    plt.xlabel('voltage / V')
    plt.grid(True)
    
    ax4 = fig1.add_subplot(224)
    l4, = ax4.plot (v, w_Wh)
    plt.title('voltage - energy dependency')
    plt.ylabel('Energy / Wh')
    plt.xlabel('voltage / V')
    plt.grid(True)
    
    # plt.xlim(xmin, xmax)
    # plt.ylim(ymin, ymax)
    plt.show()

#-----------------------------------------------------------------------------------
def print_text(text, addline_numbers = True, ignore_comment_numbers = True):
    if addline_numbers:
        lines = text.split('\n')
        i = 0
        for line in lines:
            if addline_numbers:
                line = line.strip()
                if line:
                    if '#' in line[:3]:
                        if ignore_comment_numbers:
                            print('\t', line)
                        else:
                            print(i, ":\t", line)
                            i += 1            
                    else:        
                        print(i, ":\t", line)
                        i += 1
    else: 
        print(text)        

#-------------------------------------------------------------------------- 

    
def plot_from_pico():   
    pico1 = Pico("SOMCA")
    pico1.connect()
    text = pico1.read_file("values.dat",  printflag = False)
    length = len(text)
    print_text(text, ignore_comment_numbers = True)
    
    filetools = Filetools("../data", "values.dat")
    filetools.ask_filename_save()
    filetools.ask_comment()
    filetools.save_data(text)
    
    print("File size: ", length, "characters")
    
    print("Data from SOMCA hardware device")

    plot_all(text, "Direct from SOMCA  ")
    pico1.close()
    
    
def plot_stored():
    filetools = Filetools("../data", "values.dat")
    filetools.ask_filename_read_list()
    text = filetools.read_data()
    
    length = len(text)
    print_text(text, ignore_comment_numbers = True)
    
    print("File size: ", length, "characters")
    print("Plot from stored data on computer")
    
    plot_all(text, "STORED DATA  ")
 

#---------------------------------------------------------

# MAIN:
print("SOMCA data downloader and plotter")

choice = input("Read from hardware <Enter> or stored data (any key)?")
if choice:
    plot_stored()
else:    
    plot_from_pico()



    
    
    
