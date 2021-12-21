import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import glob, pprint, sys, os

def to_basename(p):
  return os.path.basename(p).lower()

def collect_files_from_directory(dir, accepts=[".jpg", ".png", ".jpeg"]):
  hashmap = {}
  for f in glob.glob(f'{dir}/**/*', recursive=True):
    for ending in accepts:
      if(f.lower().endswith(ending)):
        print("image found")
        basename = to_basename(f)
        if basename not in hashmap:
          hashmap[basename] = []
        hashmap[basename].append(f)

  pprint.pprint(hashmap)
  return hashmap
  
def toggle_image(var,filename):
  # loop through all the buttons to enable or disable each one
  for key, val in refs[to_basename(filename)][DUPLICATES].items():
    print(key)
    print(val)
    if val['idx']==var:
      print("flipping ", var)
      refs[to_basename(filename)][DUPLICATES][key]['save'] = not refs[to_basename(filename)][DUPLICATES][key]['save'] 

    color = "red"
    if refs[to_basename(filename)][DUPLICATES][key]['save']:
      color = "black"

    refs[to_basename(filename)][DUPLICATES][key]['btn_ref'].config(fg=color)

first_key = lambda d: list(d.keys())[0]
root = tk.Tk()
root.geometry("600x450")
images_mapping = collect_files_from_directory('images') 
refs = {}
current_page_idx = first_key(images_mapping)

DOOMSDAY_COUNT = "doomsday_count"
DUPLICATES = 'duplicates'

def undo():
  pass

def advance(curr_idx):
  # increment doomsday on the doomed baskets
  for key, val in refs.items():
    if DOOMSDAY_COUNT not in val:
      refs[key][DOOMSDAY_COUNT] = 0

    if key == curr_idx or DOOMSDAY_COUNT in val:
      if val[DOOMSDAY_COUNT] > 1 or key == curr_idx:
        print("hooo")
        refs[key][DOOMSDAY_COUNT] += 1
      else:
        refs[key][DOOMSDAY_COUNT] = 0

  # advance pointer
  unviewed = [x for x in images_mapping if x not in refs or not refs[x][DOOMSDAY_COUNT] > 0]

  curr_idx = None
  if len(unviewed) > 0:
    curr_idx = unviewed[0]

  draw_buttons(curr_idx)


var = 0 



print('refs', refs)
print('im map', images_mapping)
filename = current_page_idx

def draw_buttons(filename):
  print('drawing buttnso fro ', filename)
  if filename:
    for i in range(len(images_mapping[filename])):
      image_path = images_mapping[filename][i]
      img_file = Image.open(image_path)
      img_file = img_file.resize((150, 150))
      img = ImageTk.PhotoImage(img_file)
      btn = tk.Button(
          root, 
          image=img,
          text=image_path,
          compound=tk.BOTTOM,
          command=lambda var=i, path=image_path:toggle_image(var,path),
          fg="red"
      )
      btn.grid(row=1,column=i)

      if filename not in refs:
        refs[filename] = {
          DUPLICATES: {},
          DOOMSDAY_COUNT: 0,
        }

      refs[filename][DUPLICATES][image_path] = {
        "idx": i,
        "image_ref": img,
        "btn_ref": btn,
        "save": False,
      }
      
btn = tk.Button(
  root, 
  text="Advance ->",
  command=lambda: advance(current_page_idx),
)
btn.grid(row=1,column=1)

root.mainloop()