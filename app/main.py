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

def advance_pointer(increment=False):
  available = [x for x in images_mapping if x not in refs or not refs[x][DOOMSDAY_COUNT] > 0 and len(refs[x][DUPLICATES].keys()) > 0]
  curr_idx = None
  if len(available) > 0:
    has_doomsday_at_one = [x for x in images_mapping if x in refs and refs[x][DOOMSDAY_COUNT] == 1 and len(refs[x][DUPLICATES].keys()) > 0]
    if len(has_doomsday_at_one) > 0:
      curr_idx = has_doomsday_at_one[-1]
    else:
      curr_idx = available[0]
    print("available: ", curr_idx)
  else:
    has_big_doomsday = [x for x in images_mapping if refs[x][DOOMSDAY_COUNT] > 0 and len(refs[x][DUPLICATES].keys()) > 0]
    if len(has_big_doomsday) > 0:
      curr_idx = has_big_doomsday[-1]
    print("unavailable")

  if increment:
    if curr_idx not in refs:
      refs[curr_idx] = {
        DOOMSDAY_COUNT: 0,
        DUPLICATES: {},
      }
    refs[curr_idx][DOOMSDAY_COUNT] += 1


  draw_buttons(curr_idx)
  pprint.pprint(refs)

def undo(current_page_idx):
  curr_index = images_mapping_keys.index(current_page_idx)

  for key in images_mapping_keys:
    if images_mapping_keys.index(key) <= curr_index:
      refs[key][DOOMSDAY_COUNT] -= 1

      if refs[key][DOOMSDAY_COUNT] < 0:
        refs[key][DOOMSDAY_COUNT] = 0

  advance_pointer()

def advance(current_page_idx):
  # increment doomsday on the doomed baskets

  if(current_page_idx):
    curr_index = images_mapping_keys.index(current_page_idx)
  else:
    curr_index = -1

  for key in images_mapping_keys:
    if images_mapping_keys.index(key) <= curr_index:
      refs[key][DOOMSDAY_COUNT] += 1

    if key in refs and refs[key][DOOMSDAY_COUNT] > 2:
      keep = {}
      for filename, val in refs[key][DUPLICATES].items():
        if not val['save']:
          if os.path.exists(filename):
            os.remove(filename)
        else:
          keep[filename] = val
      print("keeeep", keep)
      refs[key][DUPLICATES] = keep

        
  advance_pointer(increment=True)

def get_color(id1, id2):
  if id2 in refs[id1][DUPLICATES] and "save" in refs[id1][DUPLICATES][id2] and refs[id1][DUPLICATES][id2]['save']:
    return "black"
  else:
    return "red"

def draw_buttons(current_page_idx):
  for widget in root.winfo_children():
    widget.destroy()
  
  undo_button = tk.Button(
    root, 
    text="<- Undo",
    command=lambda: undo(current_page_idx),
  )
  undo_button.grid(row=1,column=1)

  advance_button = tk.Button(
    root, 
    text="Advance ->",
    command=lambda: advance(current_page_idx),
  )
  advance_button.grid(row=1,column=2)

  if current_page_idx:
    # add current page to refs
    if current_page_idx not in refs:
      refs[current_page_idx] = {
        DUPLICATES: {},
        DOOMSDAY_COUNT: 0,
      }

    for i in range(len(images_mapping[current_page_idx])):
      image_path = images_mapping[current_page_idx][i]

      # add specific image to memory
      if image_path not in refs[current_page_idx][DUPLICATES]:
        refs[current_page_idx][DUPLICATES][image_path] = {
          "idx": i,
          "image_ref": None,
          "btn_ref": None,
          "save": False,
        }
      else:
        if len(refs[current_page_idx][DUPLICATES].keys()) == 0:
          continue

      # cache the image ref
      if os.path.exists(image_path):
        if refs[current_page_idx][DUPLICATES][image_path]['image_ref']:
          img = refs[current_page_idx][DUPLICATES][image_path]['image_ref']
        else:
          img_file = Image.open(image_path)
          img_file = img_file.resize((150, 150))
          img = ImageTk.PhotoImage(img_file)
          refs[current_page_idx][DUPLICATES][image_path]['image_ref'] = img
      else:
        img = None

      # create the button
      btn = tk.Button(
          root, 
          image=img,
          text=image_path,
          compound=tk.BOTTOM,
          command=lambda var=i, path=image_path:toggle_image(var,path),
          fg=get_color(current_page_idx, image_path)
      )
      btn.grid(row=2,column=i)

      #cache the button
      refs[current_page_idx][DUPLICATES][image_path]['btn_ref'] = btn

      

# set up tkinter
root = tk.Tk()
root.geometry("600x450")

# pull images
images_mapping = collect_files_from_directory('images') 
images_mapping_keys = list(images_mapping.keys())

print("mapping,", images_mapping_keys)

# memory for application
refs = {}

DOOMSDAY_COUNT = "doomsday_count"
DUPLICATES = 'duplicates'

draw_buttons(None)




root.mainloop()