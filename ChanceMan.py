import random, sys, urllib.request, io, webbrowser, threading
import tkinter as tk
from tkinter import messagebox
import configparser
import pyglet
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
from requests import get

# -----------------------
# Theme
# -----------------------

BG_MAIN = "#2b2b2b"
BG_DARK = "#1f1f1f"
BG_BORDER = "#3a3a3a"
FG_TEXT = "#e6e6e6"
ACCENT = "#8e764c"

# -----------------------
# Font
# -----------------------

pyglet.options["win32_gdi_font"] = True
pyglet.font.add_file("resources/runescape_uf.ttf")

# -----------------------
# Image loader (async)
# -----------------------

class WebImage:
    def __init__(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as u:
            raw = u.read()
        image = Image.open(io.BytesIO(raw))
        image = image.resize((250, 250), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(image)

    def get(self):
        return self.image


def load_image_async(choice):
    def task():
        try:
            img = WebImage(findPic(choice)).get()
            root.after(0, update_icon, img)
        except:
            print("Failed to find image!")

    threading.Thread(target=task, daemon=True).start()


def update_icon(img):
    icon_label.configure(image=img)
    icon_label.image = img


# -----------------------
# Wiki scraping
# -----------------------

def getdata(url):
    return get(url).text


def findPic(choice):
    if choice[len(choice)-1]==" ":
        choice = choice[:len(choice)-1]
    wikiUrl = f"https://runescape.wiki/w/{choice.replace(' ', '_')}"
    soup = BeautifulSoup(getdata(wikiUrl), "html.parser")

    imgs = [
        "https://runescape.wiki" + img["src"]
        for img in soup.find_all("img")
        if img.get("src")
    ]
    return imgs[1] if len(imgs) > 1 else imgs[0]


# -----------------------
# App logic
# -----------------------

def roll():
    global unlocked, items

    if not items:
        messagebox.showinfo("Done", "No items left!")
        return

    choice = random.choice(items)
    cQuery = choice
    items.remove(choice)
    unlocked.append(choice)

    if len(choice) > 20:
        parts = choice.split(" ")
        match len(parts):
            case 2:
                choice = f"{parts[0]} \n{parts[1]}"
            case 3:
                choice = f"{parts[0]} {parts[1]} \n{parts[2]}"
            case 4:
                choice = f"{parts[0]} {parts[1]} \n{parts[2]} {parts[3]}"
            case _:
                choice = parts

    unlock_var.set(choice)
    unlocked_listbox.insert(tk.END, choice)
    
    print("Attempting to find image...")
    load_image_async(cQuery)


def wiki():
    try:
        item = unlocked_listbox.get(unlocked_listbox.curselection())
        webbrowser.open(f"https://runescape.wiki/w/{item.replace(' ', '_')}")
    except:
        webbrowser.open("https://runescape.wiki/")


def close():
    with open("resources/Unlocks.txt", "w") as f:
        for item in unlocked:
            f.write(item + "\n")
    root.destroy()
    sys.exit()


# -----------------------
# Dragging logic
# -----------------------

def start_move(event):
    root.x = event.x
    root.y = event.y


def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")


# -----------------------
# Config + data
# -----------------------

config = configparser.ConfigParser()
config.read("config.ini")

items, unlocked = [], []

with open("resources/RS3Tradeables.txt") as f:
    items = [l.strip() for l in f]

with open("resources/Unlocks.txt") as f:
    unlocked = [l.strip() for l in f]

for u in unlocked:
    if u in items:
        items.remove(u)

if not config["DEFAULT"].getboolean("complex_mode"):
    items = [i for i in items if "(" not in i]
    items = [i for i in items if "+" not in i]

if config["DEFAULT"].getboolean("ftop_mode"):
    with open("resources/FTPItems.txt") as f:
        ftp = [l.strip() for l in f]
    items = [i for i in items if i in ftp]
    
# -----------------------
# UI
# -----------------------

root = tk.Tk()
root.geometry("708x508")
root.overrideredirect(True)
root.configure(bg=BG_BORDER)
root.iconbitmap("resources/appicon.ico")

# Title bar
title_bar = tk.Frame(root, bg=BG_DARK, height=32)
title_bar.pack(fill="x")
title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)

tk.Label(
    title_bar,
    text="ChanceMan RS3",
    bg=BG_DARK,
    fg=FG_TEXT,
    font=("Runescape UF", 14)
).pack(side="left", padx=10)

close_btn = tk.Button(
    title_bar,
    text="✕",
    bg=BG_DARK,
    fg=FG_TEXT,
    borderwidth=0,
    command=close,
    font=("Arial", 12)
)
close_btn.pack(side="right", padx=10)

# Main container
main = tk.Frame(root, bg=BG_MAIN)
main.pack(fill="both", expand=True)

# Left panel
left = tk.LabelFrame(
    main,
    text="Unlocked Items",
    bg=BG_MAIN,
    fg=FG_TEXT,
    font=("Runescape UF", 12)
)
left.pack(side="left", fill="y", padx=8, pady=8)

unlocked_listbox = tk.Listbox(
    left,
    bg=BG_DARK,
    fg=FG_TEXT,
    width=34,
    highlightthickness=0
)
unlocked_listbox.pack(fill="both", expand=True)

for item in unlocked:
    unlocked_listbox.insert(tk.END, item)

# Right panel
right = tk.Frame(main, bg=BG_MAIN)
right.pack(side="left", fill="both", expand=True)

icon_label = tk.Label(right, bg=BG_MAIN)
icon_label.pack(pady=12)

tk.Label(
    right,
    text="You unlocked:",
    bg=BG_MAIN,
    fg=FG_TEXT,
    font=("Runescape UF", 24)
).pack()

unlock_var = tk.StringVar(value="<Roll result will appear here>")
tk.Label(
    right,
    textvariable=unlock_var,
    bg=BG_MAIN,
    fg=FG_TEXT,
    font=("Runescape UF", 20)
).pack(pady=8)

btns = tk.Frame(right, bg=BG_MAIN)
btns.pack(pady=10)

tk.Button(
    btns,
    text="Roll Item",
    font=("Runescape UF", 18),
    command=roll
).pack(side="left", padx=10)

tk.Button(
    btns,
    text="Open Wiki",
    font=("Runescape UF", 18),
    command=wiki
).pack(side="left", padx=10)

root.mainloop()
