import tkinter as tk
from tkinter import messagebox
import sys
from PIL import Image, ImageTk

# from .utilities.utils import collect_files_from_directory
# for i in range(len(images)):
#   img_file = Image.open(images[i])
#   img_file = img_file.resize((150, 150))
#   img = ImageTk.PhotoImage(img_file)
#   b = tk.Button(
#       root, 
#       image=img,
#       text=images[i],
#       compound=tk.BOTTOM,
#       command=lambda: handleClick(images[i])
#   )
#   b.grid(row=1, column=i)
 

root = tk.Tk()
root.geometry("600x450")
def main(event):
  print(event.widget)


images = ["images/stock1.jpeg","images/stock2.jpeg","images/person1.jpeg"]


def show_lan(var,path):
  # buttonse
  
    #loop through all the buttons to enable or disable each one
    for i in range(len(buttons)):
        if i==var:
            buttons[i].config(state="disabled")
        else:
            buttons[i].config(state="normal")
var = 0

buttons = [] # to store button references 
#command=lambda index=index, n=n: appear(index, n)
for image in images:
    btn = tk.Button(root, text=image, command=lambda var=var, path=images[i]:toggle_image(var,path))
    btn.grid(row=1,column=var)
    var += 1
    buttons.append(btn)  # adding button reference 
    
root.mainloop()



root.mainloop()