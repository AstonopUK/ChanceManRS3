# Designed by B.Hopgood 2026
#Importing libraries
import random, time, subprocess, sys, urllib.request, io, webbrowser
try:
    from guizero import *
    import configparser
    import pyglet
    from PIL import ImageTk, Image
    from bs4 import *
    from requests import *
except ImportError:
    subprocess.check_call([sys.executable,"-m","pip","install","guizero"])
    subprocess.check_call([sys.executable,"-m","pip","install","pyglet"])
    subprocess.check_call([sys.executable,"-m","pip","install","pillow"])
    subprocess.check_call([sys.executable,"-m","pip","install","bs4"])
    subprocess.check_call([sys.executable,"-m","pip","install","requests"])
    subprocess.check_call([sys.executable,"-m","pip","install","configparser"])
finally:
    print("NB: If a package install was required, restart the app.")

def roll(text):
    global unlocked, items
    choice = random.choice(items)
    unlocked.append(choice)
    items.remove(choice)
    
    text.value=choice
    unlockedList.append(choice)
    img = WebImage(findPic(choice)).get()
    icon.image=img

def getdata(url): 
    r = get(url) 
    return r.text

def wiki():
    try:
        formatchoice = unlockedList.value.replace(" ","_")
        wikiUrl = "https://runescape.wiki/w/"+formatchoice
        webbrowser.open(wikiUrl)
    except:
        webbrowser.open("https://runescape.wiki/")
        
def close():
    for z in range(len(unlocked)-1):
        unlocked[z] = unlocked[z]+"\n"
    f = open("resources/Unlocks.txt", "w")
    f.writelines(unlocked)
    f.close()
    quit()
    
def findPic(choice):
    formatchoice = choice.replace(" ","_")
    wikiUrl = "https://runescape.wiki/w/"+formatchoice
    htmldata = getdata(wikiUrl) 
    soup = BeautifulSoup(htmldata, 'html.parser')
    imgLinks = []
    for item in soup.find_all('img'):
        imgLinks.append("https://runescape.wiki"+item["src"])
    return imgLinks[1]

pyglet.options['win32_gdi_font'] = True
fontpath = "resources/runescape_uf.ttf"
pyglet.font.add_file(fontpath)

class WebImage:
    def __init__(self, myurl):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        url = urllib.request.Request(myurl, headers=headers)
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        image = image.resize((250,250), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(image)

    def get(self):
        return self.image

#Import config
config = configparser.ConfigParser()
config.read('config.ini')
print("Complex mode is set to:",config["DEFAULT"]["complex_mode"])

#Init var
unlocked = []
items = []

#Read from data files
with open("resources/RS3Tradeables.txt") as f:
    for line in f:
        line=line.replace("\n","")
        items.append(line)  
with open("resources/Unlocks.txt") as f:
    for line in f:
        line=line.replace("\n","")
        unlocked.append(line)

#Removing unlocked items from pool
for item in unlocked:
    if item in items:
        items.remove(item)

#Setup default mode if complex mode disabled (disabled by default)
if config["DEFAULT"]["complex_mode"] == False:
    optional = []
    for item in items:
        if "(" in item:
            optional.append(item)
            items.remove(item)

#Init app
app = App(title="ChanceMan RS3", width=700, height=500)
app.bg = "#94866d"
app.font= "Runescape UF"
app.tk.iconbitmap("resources/appicon.ico")
app.tk.protocol("WM_DELETE_WINDOW", close)

#Layout
leftBox = TitleBox(app, text="Unlocked Items", align="left", height="fill", width=275)
rightBox = Box(app, align="left", height="fill", width="fill")
unlockedList = ListBox(leftBox, height="fill", width="fill", items = unlocked, scrollbar=True)
unlockedList.bg = "#cfc08d"
spacer = Box(rightBox, height=30, width="fill")
try:
    img = WebImage("ttps://runescape.wiki/images/thumb/Random_event_gift_detail.png/217px-Random_event_gift_detail.png?049db").get()
    icon = Picture(rightBox,image=img)
except:
    icon = Picture(rightBox)
staticText = Text(rightBox, text="You unlocked: ", size=24)
unlockText = Text(rightBox, text="<Roll result will appear here>\n", size=20)
btnBox = Box(rightBox)
rollBtn = PushButton(btnBox, align="left", text="Roll Item", command=lambda:roll(unlockText))
rollBtn.text_size = 20
wikiBtn = PushButton(btnBox, align="left", text="Open Wiki", command=wiki)
wikiBtn.text_size = 20
app.display()