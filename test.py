import tkinter as tk
my_w = tk.Tk()
my_w.geometry("300x200")  # Size of the window 
my_w.title("www.plus2net.com")  # Adding a title

my_str = tk.StringVar()
l1 = tk.Label(my_w,  textvariable=my_str, width=10 )
l1.grid(row=0,column=2,columnspan=6) 

def show_lan(my_language,var):
    my_str.set(my_language)
    #loop through all the buttons to enable or disable each one
    for i in range(len(buttons)):
        if i==var:
            buttons[i].config(state="disabled")
        else:
            buttons[i].config(state="normal")

list_languages = ("PHP","Python","HTML","Tkinter","Pandas")
var = 0

buttons = [] # to store button references 
#command=lambda index=index, n=n: appear(index, n)
for language in list_languages:
    btn = tk.Button(my_w, text=language, command=lambda var=var,lan=language:show_lan(lan,var))
    btn.grid(row=1,column=var)
    var += 1
    buttons.append(btn)  # adding button reference 
    
my_w.mainloop()