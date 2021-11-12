import os
import os.path
import tkinter
from tkinter.constants import CENTER, NW, SE, SW,TOP
from PIL import ImageTk, Image
from deduplicate import clean_downloads


clean_downloads()

file_list = os.listdir("./dataset")
# file_list = [i for i in file_list if "_2" not in i and "captcha" not in i and "6" in i]

window = tkinter.Tk()
window.geometry("370x230")

i = 0
window.title(file_list[i])
window.eval('tk::PlaceWindow . center')
window.resizable(width=False, height=False)

image = Image.open(f"dataset/{file_list[i]}")
image = image.resize((370, 115), Image.ANTIALIAS)
image = ImageTk.PhotoImage(image)

label = tkinter.Label(window, image = image)
label.pack(side=TOP, anchor=NW)

inputbox = tkinter.StringVar()  
captcha_letters = tkinter.Entry(window, textvariable="inputbox", justify="center", font=("Calibri",60), width=8, bg="light blue")
captcha_letters.insert(0,file_list[i][0:6].upper())
captcha_letters.place(x=0, y=115)

def next_captcha(event):
    if len(captcha_letters.get()) == 6:
        global i
        old_name = f"dataset/{file_list[i]}"
        new_name = f"temp_dataset/{captcha_letters.get().lower()}.jpeg"
        print(old_name, new_name)
        os.rename(old_name, new_name)
        
        i += 1
        window.title(file_list[i])
        captcha_letters.delete(0,tkinter.END)
        # captcha_letters.insert(0,file_list[i][0:6].upper())
        image = Image.open(f"dataset/{file_list[i]}")
        image = image.resize((370, 115), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        label.configure(image=image)
        label.image = image
    

window.bind("<Return>", next_captcha)

label.pack()

window.mainloop()

