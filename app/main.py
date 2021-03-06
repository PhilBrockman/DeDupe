def vprint(*args, always=True):
  if always:
    print(args)
  else:
    if CURRENT["VERBOSE"]:
      print(args)

def setIndex(val):
  print("setting index", val)
  CURRENT[INDEX] = val

def to_basename(p):
  return os.path.basename(p).lower()

def collect_files_from_directory(dir, accepts=[".jpg", ".jpeg", ".mp4"]):
  val = 0
  hashmap = {}
  for f in glob.glob(dir, recursive=True):
    val += 1
    if val % 1000 == 0:
      vprint(val)
    for ending in accepts:
      if(f.lower().endswith(ending)):
        # vprint("image found")
        basename = to_basename(f)
        if basename not in hashmap:
          hashmap[basename] = []
        hashmap[basename].append(f)

  return hashmap

def toggle_image(var,filename):
  # loop through all the buttons to enable or disable each one
  for key, val in CURRENT[MEM][to_basename(filename)][DUPLICATES].items():
    if val['idx']==var:
      vprint("flipping ", var)
      CURRENT[MEM][to_basename(filename)][DUPLICATES][key]['save'] = not CURRENT[MEM][to_basename(filename)][DUPLICATES][key]['save']

    color = "red"
    if CURRENT[MEM][to_basename(filename)][DUPLICATES][key]['save']:
      color = "black"

    CURRENT[MEM][to_basename(filename)][DUPLICATES][key]['btn_ref'].config(fg=color)

def file_age(filepath):
  if os.path.exists(filepath):
    return time.time() - os.path.getmtime(filepath)
  else:
    return time.time() 

def get_clamped_images_mapping():
  res = {x: CURRENT['images_mapping'][x] for x in CURRENT['images_mapping'] if x not in CURRENT[CLAMPED_KEY_LIST]}
  # pprint.pprint(res)
  return res

def clamped_keys():
  remaining_keys = list(get_clamped_images_mapping().keys())
  remaining_keys.sort()
  return remaining_keys

def setState(val):
  # print("current state")
  # pprint.pprint(CURRENT)
  # print("chaning to ", val)
  if val == INIT:
    CURRENT[STATE] = INIT
    init_program()
    return
  if val == RUNNING:
    CURRENT[STATE] = RUNNING
    return
  if val == END_PROGRAM:
    CURRENT[STATE] = END_PROGRAM
    end_program()
    return

def advance_pointer(advance):
  available = [x for x in clamped_keys() if x not in CURRENT[MEM] or CURRENT[MEM][x][DOOMSDAY_COUNT] <= 0]
  # vprint("available", available)
  if advance:
    # find first new image
    vprint("advancing with ", len(available), "choices")
    if len(available) > 0:
      try:
        print(" 0 case")
        setIndex(available[0])
        print(" 0--I set the index ")
      except:
        print("1) excetped in advance pointer")
        setState(END_PROGRAM)
        return
    else:
      print("2) excetped in advance pointer")
      setState(END_PROGRAM)
      return
  else:
    prev_seen = [x for x in clamped_keys() if x in CURRENT[MEM] and CURRENT[MEM][x][DOOMSDAY_COUNT] == 1]
    if len(prev_seen) > 0:
      # print("3) excetped in advance pointer")
      setIndex((prev_seen[-1]))
    elif len(available) > 0:
      # print("4) excetped in advance pointer")
      setIndex((available[0]))
    vprint("undoing with ", len(available), "choices")

  print("continuing to advance")
  # provide adefault structure for the objects in memory
  if CURRENT[INDEX] and CURRENT[INDEX] not in CURRENT[MEM]:
    CURRENT[MEM][CURRENT[INDEX]] = {
      DOOMSDAY_COUNT: 0,
      DUPLICATES: {},
    }
  
  # Onwards!
  if(advance):
    try: 
      # this will fail after falling off the end of the list
      vprint("current index", CURRENT[INDEX])
      CURRENT[MEM][CURRENT[INDEX]][DOOMSDAY_COUNT] += 1
    except:
      # we did it!
      setState(END_PROGRAM)
      return

  draw_buttons()

def undo():
  if CURRENT[STATE] == INIT:
    print("blocking UNDO()")
    return

  print("UNDO()")
  setState(RUNNING)

  remaing_keys = clamped_keys()

  for key in remaing_keys:
    if remaing_keys.index(key) <= remaing_keys.index(CURRENT[INDEX]):
      CURRENT[MEM][key][DOOMSDAY_COUNT] -= 1

  # 1 0 0 0 0 0  
  if CURRENT[MEM][remaing_keys[0]][DOOMSDAY_COUNT] == 0:
      print("the flag is up")
      setState(INIT)
      return
  else:
    print("______UUUUUU_U__U_U_U__U")


  vprint("<-- undo")
  advance_pointer(advance=False)

def save():
  for key in CURRENT[MEM].keys():
    if CURRENT[MEM][key][DOOMSDAY_COUNT] > 0:
      DELETE_UNSAVED_DUPLICATE_PHOTOS(key)
    if key == CURRENT[INDEX]:
      for im_path in CURRENT[MEM][key][DUPLICATES]:
        CURRENT[MEM][key][DUPLICATES][im_path]['btn_ref'].config(text=CURRENT[MEM][key][DUPLICATES][im_path]['save_location'])

  CURRENT[CLAMPED_INDEX] += clamped_keys().index(CURRENT[INDEX])
  sorted_keys = list(CURRENT['images_mapping'].keys())
  sorted_keys.sort()
  CURRENT[CLAMPED_KEY_LIST] = sorted_keys[:CURRENT[CLAMPED_INDEX]]
  with open(SAVE_CLAMPED_INDEX_FILE, 'w') as filetowrite:
      filetowrite.write(str(CURRENT[CLAMPED_INDEX]))

def DELETE_UNSAVED_DUPLICATE_PHOTOS(key):
  if key in CURRENT[CLAMPED_KEY_LIST]:
    return "out of bounds"

  keep = {}
  for original_filename in CURRENT[MEM][key][DUPLICATES]:
    val = CURRENT[MEM][key][DUPLICATES][original_filename]
    if not val['save']:
      if os.path.exists(original_filename):
        os.remove(original_filename)
    else:
      path = os.path.dirname(val['save_location'])
      if not os.path.exists(path):
        os.makedirs(path)
      try:
        shutil.move(val['original_location'], val['save_location'])
      except:
        print("could not move", val)
        messagebox.showerror("Error moving file", f"This file could not be moved: {val['original_location']}. Have Phil take a look at the command line history to try to diagnose what happened. In the meantime, try to see if the rest of the files on this page are in the location you expect. There's a chance restarting the program could help, but I really don't know what happened.\n\nFull details: {val}")

      
      val['original_location'] = val['save_location']
      keep[original_filename] = val

  CURRENT[MEM][key][DUPLICATES] = keep

def advance():
  # don't let the end advance
  if CURRENT[STATE] == END_PROGRAM:
    print("blocking advance()")
    return
  print("ADVANCE()")
  setState(RUNNING)

  remaining_keys = clamped_keys()
  # print("advancing: ", remaining_keys)
  if CURRENT[INDEX] is not None:
    print("current index is not noen")
    for key in remaining_keys:
      if remaining_keys.index(key) <= remaining_keys.index(CURRENT[INDEX]):
        print("\t advancing ", key)
        CURRENT[MEM][key][DOOMSDAY_COUNT] += 1

      if key in CURRENT[MEM] and CURRENT[MEM][key][DOOMSDAY_COUNT] > CURRENT[UNDO_WINDOW]:
        DELETE_UNSAVED_DUPLICATE_PHOTOS(key)

  vprint("--> advance")
  advance_pointer(advance=True)

def get_color(id1, id2):
  if id2 in CURRENT[MEM][id1][DUPLICATES] and "save" in CURRENT[MEM][id1][DUPLICATES][id2] and CURRENT[MEM][id1][DUPLICATES][id2]['save']:
    return "black"
  else:
    return "red"

def add_current_index_to_memory():
  if not CURRENT[INDEX]:
    return

  duplicates = get_clamped_images_mapping()[CURRENT[INDEX]]
  if len(duplicates) >= 1:
    first_key = get_clamped_images_mapping()[CURRENT[INDEX]][0]
    youngest_file = {
      "key": first_key,
      "age": file_age(first_key)
    }

    for key in duplicates:
      key_age = file_age(key)
      if key_age >= youngest_file['age']:
        youngest_file['key'] = key
        youngest_file['age'] = key_age

  for i in range(len(get_clamped_images_mapping()[CURRENT[INDEX]])):
    image_path = get_clamped_images_mapping()[CURRENT[INDEX]][i]

    # add specific image to memory
    if image_path not in CURRENT[MEM][CURRENT[INDEX]][DUPLICATES]:
      CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path] = {
        "idx": i,
        "image_ref": None,
        "btn_ref": None,
        "save": image_path == youngest_file['key'],
        "save_location": image_path,
        "original_location": image_path,
      }
    else:
      if len(CURRENT[MEM][CURRENT[INDEX]][DUPLICATES].keys()) == 0:
        continue

    button_text = f"<deleted> @ {image_path}"
    image_location = CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['save_location']
    # cache the image ref
    if os.path.exists(image_location):
      if CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['image_ref']:
        img = CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['image_ref']
      else:
        try:
          img_file = Image.open(image_location)
          img_file = img_file.resize((CURRENT[WIDTH], CURRENT[HEIGHT]))
          img = ImageTk.PhotoImage(img_file)
          CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['image_ref'] = img
        except:
          button_text = f"Cannot Load: {image_path}"
          CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['image_ref'] = None
      button_text = image_path
    else:
      img = None

    # create the button
    btn = tk.Button(
        content_frame,
        image=img,
        text=button_text,
          wraplength=180,
        compound=tk.BOTTOM,
        command=lambda var=i, path=image_path:toggle_image(var,path),
        fg=get_color(CURRENT[INDEX], image_path)
    )
    btn.grid(row=2 + 3*(i // CURRENT["COLUMNS"]), column=i%CURRENT["COLUMNS"])

    # allow path to be rewritten
    def setSaveLocation(im_p, new_location):
      CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][im_p]['save_location'] = new_location
    path_input = tk.Text(
      content_frame,
      width = 40,
      height = 5,
      )
    path_input.grid(row=3 + 3*(i // CURRENT["COLUMNS"]), column=i%CURRENT["COLUMNS"])
    path_input.insert(tk.END, CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['save_location'])
    path_input.bind("<KeyRelease>", lambda x, image_path=image_path: setSaveLocation(image_path, x.widget.get("1.0",'end-1c')))

    # open full screen preview
    def create_window(img_location):
      koniec=tk.Toplevel(width=1200, height=800)
      koniec.title("V??taz!")

      created_window = Example(koniec)
      created_window.pack(side="top", fill="both", expand=True)

      img = ImageTk.PhotoImage(Image.open(img_location))
      label = tk.Label(created_window.frame, image=img)
      label.image = img # keep a reference!
      label.pack()


    preview_btn = tk.Button(content_frame, text="preview in new window")
    preview_btn.bind("<Button-1>", lambda e, loc=CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['original_location']: create_window(loc))
    preview_btn.grid(row=4 + 3*(i // CURRENT["COLUMNS"]), column=i%CURRENT["COLUMNS"])

    #cache the button
    CURRENT[MEM][CURRENT[INDEX]][DUPLICATES][image_path]['btn_ref'] = btn

def undo_button(row, column):
  undo_button = tk.Button(
    content_frame,
    text="<- Undo",
    command=undo,
  )
  undo_button.grid(row=row,column=column)

def save_button(row, column):
  save_button = tk.Button(
    content_frame,
    text="[save]",
    command=save,
  )
  save_button.grid(row=row,column=column)

def advance_button(row, column):
  advance_button = tk.Button(
    content_frame,
    text="Advance ->",
    command=lambda: advance(),
  )
  advance_button.grid(row=row,column=column)

def draw_buttons():
  print("drawing buttons")
  for widget in content_frame.winfo_children():
    widget.destroy()

  undo_button(row=1, column=1)
  save_button(row=1, column=2)
  advance_button(row=1, column=3)
  label = tk.Message(
    content_frame,
    text=f"Basket {CURRENT[INDEX]} ({1 + clamped_keys().index(CURRENT[INDEX]) + CURRENT[CLAMPED_INDEX] } / {len(CURRENT['images_mapping'])})\n\nClamped: {CURRENT[CLAMPED_INDEX]}"
  )
  label.grid(row=1,column=4)

  add_current_index_to_memory()

def fresh_start():
  return {
      DOOMSDAY_COUNT: 0,
      DUPLICATES: {}
    }

def init_program():
  'screen for initial state'

  vprint('init_progarm()')

  for widget in content_frame.winfo_children():
    widget.destroy()
  
  setIndex(None)
  # load structure into memory
  for current_page_idx in get_clamped_images_mapping():
    CURRENT[MEM][current_page_idx] = fresh_start()

  advance_button(row=1,column=1)
  label = tk.Message(
    content_frame,
    text="Start ->"
  )
  label.grid(row=1,column=2)

def end_program():
  for widget in content_frame.winfo_children():
    widget.destroy()

  
  undo_button(row=1,column=1)
  save_button(row=1,column=2)
  label = tk.Message(
    content_frame,
    text="End of program"
  )
  label.grid(row=1,column=3)
  CURRENT['STATE'] = END_PROGRAM


import tkinter as tk
class Example(tk.Frame):
  def __init__(self, parent):

      tk.Frame.__init__(self, parent)
      self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
      self.frame = tk.Frame(self.canvas, background="#ffffff")
      self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
      self.canvas.configure(yscrollcommand=self.vsb.set)
      self.vsb.pack(side="right", fill="y")

      self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
      self.canvas.configure(xscrollcommand=self.hsb.set)
      self.hsb.pack(side="bottom", fill="x")

      self.canvas.pack(side="left", fill="both", expand=True)
      self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                tags="self.frame")

      self.frame.bind("<Configure>", self.onFrameConfigure)

  def onFrameConfigure(self, event):
      '''Reset the scroll region to encompass the inner frame'''
      self.canvas.configure(scrollregion=self.canvas.bbox("all"))

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import glob, pprint, os, sys, getopt, time, shutil

# set up tkinter
root = tk.Tk()
root.geometry("1200x900")


example = Example(root)
example.pack(side="top", fill="both", expand=True)
content_frame = example.frame
# content_frame.pack( side = tk.TOP )

SAVE_CLAMPED_INDEX_FILE = "clamped.txt"

END_PROGRAM = "end_program"
INIT = "init"
RUNNING = "running"
END_PROGRAM = "end_Program"
UNDO_WINDOW = "undo window"
STATE = "STATE"
INDEX = "index"
MEM = 'mem'
CLAMPED_INDEX = "clamp"
CLAMPED_KEY_LIST = "clamped key list"
WIDTH = 'width'
HEIGHT = 'height'

CURRENT= {
  INDEX: None,
  "DIR": ".\\**\\*",
  "COLUMNS": 5,
  WIDTH: 350,
  HEIGHT: 250,
  UNDO_WINDOW: 1,
  STATE: INIT,
  MEM: {},
  "VERBOSE": False,
  CLAMPED_INDEX: 0,
  CLAMPED_KEY_LIST: [],
}

if os.path.exists(SAVE_CLAMPED_INDEX_FILE):
  with open(SAVE_CLAMPED_INDEX_FILE) as f:
    lines = f.readlines()
  CURRENT[CLAMPED_INDEX] = int(lines[0].strip())

# pull images
if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hc:d:w:a:",["columns=","directory=","undo-window=","anchor="])
  except getopt.GetoptError:
    vprint ('main.py -c <columns> -d <directory>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
        vprint ('main.py -c <columns> -d <directory> -w <undo-window> -a <anchor>')
        sys.exit()
    elif opt in ("-c", "--columns"):
        CURRENT["COLUMNS"] = int(arg)
    elif opt in ("-d", "--directory"):
        CURRENT["DIR"] = arg
    elif opt in ("-w", "--undo-window"):
        CURRENT[UNDO_WINDOW] = arg
    elif opt in ("-a", "--anchor"):
        CURRENT[CLAMPED_INDEX] = int(arg)

  collected_files = collect_files_from_directory(CURRENT["DIR"])
  counts = {}
  for key, val in collected_files.items():
    idx = len(val)
    if idx not in counts:
      counts[idx] = 0
    counts[idx] += 1

  pprint.pprint(counts)
  print(sum(counts.values()))

  CURRENT['images_mapping'] = {x: collected_files[x] for x in collected_files if len(collected_files[x]) > 1}
  sorted_keys = list(CURRENT['images_mapping'].keys())
  sorted_keys.sort()
  CURRENT[CLAMPED_KEY_LIST] = sorted_keys[:CURRENT[CLAMPED_INDEX]]

  # memory for application
  DOOMSDAY_COUNT = "doomsday_count"
  DUPLICATES = 'duplicates'

  root.bind('<Left>', lambda x: undo())
  root.bind('<Right>', lambda x: advance())

  init_program()

  # # content_frame.configure(yscrollcommand=scroll.set)
  # # content_frame.pack(side=tk.LEFT)
    
  # # scroll.config(command=content_frame.yview)
  # scroll.pack(side=tk.RIGHT, fill=tk.Y)
  root.mainloop()