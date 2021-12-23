import tkinter as tk
import platform

# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.

        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )

    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")


# set up tkinter
root = tk.Tk()
root.geometry("600x450")
content_frame = tk.Frame(root)
content_frame.pack( side = tk.TOP )


from tkinter import messagebox
from PIL import Image, ImageTk
import glob, pprint, sys, os, textwrap
def to_basename(p):
  return os.path.basename(p).lower()

def collect_files_from_directory(dir, accepts=[".jpg", ".jpeg", ".mp4"]):
  val = 0
  hashmap = {}
  for f in glob.glob('D:\**\*', recursive=True):
	#val += 1
	#if val % 1000 == 0:
	#	print(val)
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
    if val['idx']==var:
      print("flipping ", var)
      refs[to_basename(filename)][DUPLICATES][key]['save'] = not refs[to_basename(filename)][DUPLICATES][key]['save']

    color = "red"
    if refs[to_basename(filename)][DUPLICATES][key]['save']:
      color = "black"

    refs[to_basename(filename)][DUPLICATES][key]['btn_ref'].config(fg=color)

def advance_pointer(advance):
  curr_idx = None
  available = [x for x in images_mapping if x not in refs or refs[x][DOOMSDAY_COUNT] == 0]
  if advance:
    # find first new image
    print("advancing with ", len(available), "choices")
    curr_idx = available[0]
  else:
    prev_seen = [x for x in images_mapping if x in refs and refs[x][DOOMSDAY_COUNT] == 1]
    if len(prev_seen) > 0:
      curr_idx = prev_seen[-1]
    elif len(available) > 0:
      curr_idx = available[0]
    print("undoing with ", len(available), "choices")

  if curr_idx and curr_idx not in refs:
    refs[curr_idx] = {
      DOOMSDAY_COUNT: 0,
      DUPLICATES: {},
    }
  
  if(advance):
    refs[curr_idx][DOOMSDAY_COUNT] += 1

  print("current index", images_mapping_keys.index(curr_idx))
  print([refs[x][DOOMSDAY_COUNT] for x in refs if DOOMSDAY_COUNT in refs[x]])
  draw_buttons(curr_idx)



def undo(current_page_idx):
  curr_index = images_mapping_keys.index(current_page_idx)

  for key in images_mapping_keys:
    if images_mapping_keys.index(key) <= curr_index:
      refs[key][DOOMSDAY_COUNT] -= 1
      if refs[key][DOOMSDAY_COUNT] < 0:
        refs[key][DOOMSDAY_COUNT] = 0

  print("<-- undo")
  advance_pointer(advance=False)

def advance(current_page_idx):
  # increment doomsday on the doomed baskets

  if(current_page_idx):
    curr_index = images_mapping_keys.index(current_page_idx)
  else:
    curr_index = -1

  print("current index", current_page_idx, "|", curr_index )

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
      refs[key][DUPLICATES] = keep

  print("--> advance")
  advance_pointer(advance=True)

def get_color(id1, id2):
  if id2 in refs[id1][DUPLICATES] and "save" in refs[id1][DUPLICATES][id2] and refs[id1][DUPLICATES][id2]['save']:
    return "black"
  else:
    return "red"

def add_to_memory(current_page_idx):
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

	button_text = "Image deleted"
    # cache the image ref
    if os.path.exists(image_path):
      if refs[current_page_idx][DUPLICATES][image_path]['image_ref']:
        img = refs[current_page_idx][DUPLICATES][image_path]['image_ref']
      else:
	    try:
          img_file = Image.open(image_path)
          img_file = img_file.resize((250, 250))
          img = ImageTk.PhotoImage(img_file)
          refs[current_page_idx][DUPLICATES][image_path]['image_ref'] = img
		except:
		  button_text = f"Cannot Load: {image_path}"
		  refs[current_page_idx][DUPLICATES][image_path]['image_ref'] = None
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
        fg=get_color(current_page_idx, image_path)
    )
    btn.grid(row=2 + i // 5, column=i%5)

    #cache the button
    refs[current_page_idx][DUPLICATES][image_path]['btn_ref'] = btn

def draw_buttons(current_page_idx):
  for widget in content_frame.winfo_children():
    widget.destroy()

  undo_button = tk.Button(
    content_frame,
    text="<- Undo",
    command=lambda: undo(current_page_idx),
  )
  undo_button.grid(row=1,column=1)

  advance_button = tk.Button(
    content_frame,
    text="Advance ->",
    command=lambda: advance(current_page_idx),
  )
  advance_button.grid(row=1,column=2)

  if current_page_idx:
    add_to_memory(current_page_idx)





# pull images
images_mapping = collect_files_from_directory('images')
images_mapping_keys = list(images_mapping.keys())

print("mapping,", images_mapping_keys)

# memory for application
refs = {}

DOOMSDAY_COUNT = "doomsday_count"
DUPLICATES = 'duplicates'





      # Now add some controls to the scrollframe.
      # NOTE: the child controls are added to the view port (scrollFrame.viewPort, NOT scrollframe itself)

      # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
      # self.





draw_buttons(None)


root.mainloop()