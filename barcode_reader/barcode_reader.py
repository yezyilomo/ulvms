import os
import tkinter
from tkinter import *
import sys 
import requests
import imgkit
import time
import json
import threading
import PIL
from PIL import Image, ImageTk
import matplotlib.figure
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

hid = { 4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 40: '', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';' , 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'  }

hid2 = { 4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 40: '', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':' , 52: '"', 53: '~', 54: '<', 55: '>', 56: '?'  }

def send_barcode(barcode_id):
    localtime=time.localtime()
    tm={
       'year': localtime.tm_year,
       'month': localtime.tm_mon,
       'day': localtime.tm_mday,
       'hour': localtime.tm_hour,
       'minute': localtime.tm_min,
    }
    current_time=json.dumps(tm)
    response=requests.post('http://127.0.0.1:8000/university/sign/', {'barcode_id': barcode_id, 'current_time': current_time})
    return response
    
def scanbarcode():
    fp = open('/dev/hidraw0', 'rb') 
    barcode_id=[]
    while True: 
        buf = fp.read(8) 
        for c in buf: 
            if c != 0:
                barcode_id.append(hid[c])
                if c==40:
                   barcode_id="".join(barcode_id)
                   response=send_barcode(barcode_id)
                   window.after(0, gui(response))
                   #window.after(0, refresh_progress())
                   barcode_id=[]
        

window=Tk()
window.geometry('880x750')
window.title("University Loan Verification Management System(ULVMS)")

panel3 = PanedWindow(window)
panel3.pack(side=TOP, anchor="c", pady=(30,20))

panel1 = PanedWindow(window)
panel1.pack(side=TOP, anchor="c", pady=0)

panel2 = PanedWindow(window)
panel2.pack(side=TOP, anchor="c", pady=20)

reg_no_lb=Label(panel1,text="Reg Number: ", bg="#02dddd", width=20, height=2, font=("Comfortaa", 20))
response_lb=Label(panel2,text="Response: ", bg="#02dddd", width=20, height=2, font=("Comfortaa", 20))
std_lb=Label(panel3,text="Student Name: ", bg="#02dddd", width=20, height=2, font=("Comfortaa", 20))

reg_no=Label(panel1,text="", bg="gray", width=40, height=2, font=("Comfortaa", 20))
response_message=Label(panel2,text="", bg="gray", width=40, height=2, font=("Comfortaa", 20))
name=Label(panel3,text="", bg="gray", width=40, height=2, font=("Comfortaa", 20))

reg_no_lb.pack(side=LEFT)
response_lb.pack(side=LEFT)
std_lb.pack(side=LEFT)

reg_no.pack(side=LEFT)
response_message.pack(side=LEFT)
name.pack(side=LEFT)

label = Label(window, bg="white")
label.pack(side=TOP, fill=X, ipady=4, pady=(0, 0) )


def get_progress():
   global label
   response=requests.get('http://127.0.0.1:8000/university/ajax-get-signing-progress/')
   response=json.loads(response.text)
   sg=response['signed_num']
   unsg=response['unsigned_num']
   fig = matplotlib.figure.Figure(figsize=(5.5,5.5))
   ax = fig.add_subplot(111)
   ax.pie([sg,unsg], autopct='%1.1f%%',  shadow=False, startangle=90, colors=[(2/255,221/255, 221/255),'gray']) 
   ax.legend(["Signed","Unsigned"])
   circle=matplotlib.patches.Circle( (0,0), 0.5, color='white')
   ax.add_artist(circle)  
   canvas = FigureCanvasTkAgg(fig, master=label)
   canvas.draw()
   canvas.get_tk_widget().pack()
   canvas.draw()
   time.sleep(3)

get_progress()

def gui(response):
    response=json.loads(response.content)
    response_message.config(text="")
    reg_no.config(text="")
    name.config(text="")
    time.sleep(0.3)
    name.config(text=response['name'])
    response_message.config(text=response['message'])
    reg_no.config(text=response['reg_no'])
 
barcode_scanner = threading.Thread(target=scanbarcode,)
barcode_scanner.deamon=True
barcode_scanner.start()
def on_closing():
    window.destroy()
    sys.exit(0)
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()


