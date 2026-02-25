

import numpy as np
import matplotlib.pyplot as plt

def text2xy(text, xcol, ycol, comment = '#'):
    """ returns numpy vectors x and y filled with data from text string
        data must be organized in columns separated by white space like TAB (0x09)
        xcol, ycol : column number for x and y values (starting from 0)  """
    
    lines=text.splitlines()
    i=0
    x=[]
    y=[]
       
    for line in lines:
        
        if len(line):
            if (line[0] != comment):
        
                columns = line.split()      #separator can be one or more " " or "\t"
                if len(columns)>=ycol:
                    data_error=0
                    try:
                        xl=float(columns[xcol])
                        
                    except:
                        data_error=1
                    
                    try:
                        yl=float(columns[ycol])
                    except:
                        data_error=2
                    
                    if data_error==0: 
                        x.append(xl)
                        y.append(yl)
                        i+=1
                        
                    else:
                        if debugflag:
                            print ("Data error in line ",i )   
                else:
                    if debugflag:
                        print ("Unsufficient data in line",i)    
    
    x=np.array(x)
    y=np.array(y) 
    return x,y        
#-------------------------------------------------------------
def pythonise_vector(xvector, xname):
    '''returns a Python line defining the vector
    e.g. "x = [0, 2.3, 5.6, ....]
    This line can be executed together with other Python statements'''
    s = xname +" = ["
    for xx in xvector:
        s+=  str(xx) + ", " 
    s += "]"    
    return s
#---------------------------------------------------------------    


#-----------------------------------------------------------------

template =  """
import matplotlib.pyplot as plt
fig1 = plt.figure()

ax1 = fig1.add_subplot(211)
l1, = ax1.plot (I,V)
plt.ylabel('U/V')

ax2 = fig1.add_subplot(212)
l2, = ax2.plot (I,P)
plt.ylabel('P/W')

plt.xlabel('I/A')

# plt.grid(True)
# plt.xlim(xmin, xmax)
# plt.ylim(ymin, ymax)
plt.show()
""" 


def make_plotscript(vectors):
    ''' Make executable Python script out of data vectors
    '''
    s = vectors
    s += template  
    return s    
