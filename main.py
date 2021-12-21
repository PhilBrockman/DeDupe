import tkinter as tk
from tkinter import messagebox
import sys
from PIL import Image, ImageTk

from utilities.utils import collect_files_from_directory

root = tk.Tk()
root.geometry("600x450")
images_mapping = collect_files_from_directory('./images') 
refs = {}
current_page_idx = 0



def toggle_image(var,path):
    # loop through all the buttons to enable or disable each one
    for key, val in refs[filename].items():
      if val['idx']==var:
        print("flipping ", var)
        refs[filename][key]['save'] = not refs[filename][key]['save'] 

      color = "red"
      if refs[filename][key]['save']:
        color = "black"

      refs[filename][key]['btn'].config(fg=color)

var = 0 


filename = 'stock1.jpeg'
if filename not in refs:
  refs[filename] = {}


for image in images_mapping[filename]:
  img_file = Image.open(image)
  img_file = img_file.resize((150, 150))
  img = ImageTk.PhotoImage(img_file)
  btn = tk.Button(
      root, 
      image=img,
      text=image,
      compound=tk.BOTTOM,
      command=lambda var=var, path=image:toggle_image(var,path),
      fg="red"
  )
  btn.grid(row=1,column=var)

  refs[filename][img] = {
    "idx": var,
    "image": img,
    "btn": btn,
    "save": False,
  }

  # always updtae last
  var += 1
    

root.mainloop()