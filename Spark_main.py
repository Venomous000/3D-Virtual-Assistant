import datetime
import pyttsx3
import speech_recognition 
import requests
from bs4 import BeautifulSoup
import os
import pyautogui
import random
import webbrowser
from plyer import notification
from pygame import mixer
import speedtest
import threading
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Voice Assistant Initialization
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voices", voices[0].id)
engine.setProperty("rate",170)

# Voice Assistant Functions
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        audio = r.listen(source,0,4)
        print("Listening.....")
        r.pause_threshold = 1
        r.energy_threshold = 300
        
    try:
        print("Understanding..")
        query  = r.recognize_google(audio,language='en-in')
        print(f"You Said: {query}\n")
    except Exception as e:
        print("Say that again")
        return "None"
    return query

def alarm(query):
    timehere = open("Alarmtext.txt","a")
    timehere.write(query)
    timehere.close()
    os.startfile("alarm.py")

# OpenGL Functions
def load_obj(filename):
    vertices = []
    faces = []
    colors = []  #List to store colors

    try:
        with open(filename, 'rb') as file:
            for line in file:
                line = line.decode('utf-8', errors='ignore')  # Decode using UTF-8 and ignore errors
                if line.startswith('v '):
                    vertices.append(list(map(float, line.strip().split()[1:])))
                    # Assign a random color for each vertex for demonstration purposes
                    colors.append([random.random(), random.random(), random.random()])
                elif line.startswith('f '):
                    face = [int(vertex.split('/')[0]) - 1 for vertex in line.strip().split()[1:]]
                    if len(face) == 3:
                        faces.append(face)
                    elif len(face) == 4:  # Convert quads to two triangles
                        faces.append([face[0], face[1], face[2]])
                        faces.append([face[0], face[2], face[3]])
        print(f"Loaded {len(vertices)} vertices and {len(faces)} faces from {filename}")
    except Exception as e:
        print(f"Error loading OBJ file: {e}")

    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    colors = np.array(colors, dtype=np.float32)  # Convert colors to a NumPy array

    return vertices, faces, colors

def draw_obj(vertices, faces, colors):
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex in face:
            glColor3fv(colors[vertex])  # Set the color for the vertex
            glVertex3fv(vertices[vertex])
    glEnd()

def setup_opengl():
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    light_pos = [1.0, 1.0, 1.0, 0.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

def render_thread():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, -2.0, -5)  # Adjust translation to center character vertically
    
    setup_opengl()

    vertices, faces, colors = load_obj('fyp.obj')
    if len(vertices) == 0 or len(faces) == 0:
        print("No vertices or faces loaded. Exiting render thread.")
        return

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(pygame.time.get_ticks() / 1000 * 30, 0, 1, 0)  # Rotate the model over time

        draw_obj(vertices, faces, colors)
        
        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)

def main_voice_assistant_logic():
    while True:
        query = takeCommand().lower()
        if "wake up" in query:
            from GreetMe import greetMe
            greetMe()

            while True:
                query = takeCommand().lower()
                if "ok" in query:
                    speak("Ok sir , You can call me anytime")
                    break
                ########## Spark the tryiology 2.2 #############
                elif "change password" in query:
                    speak("What's the new password")
                    new_pw = input("Enter the new password\n")
                    new_password = open("password.txt","w")
                    new_password.write(new_pw)
                    new_password.close()
                    speak("Done sir")
                    speak(f"Your new password is {new_pw}")
                elif "schedule my day" in query:
                    tasks = [] #Empty list 
                    speak("Do you want to clear old tasks (Plz speak YES or NO)")
                    query = takeCommand().lower()
                    if "yes" in query:
                        file = open("tasks.txt","w")
                        file.write(f"")
                        file.close()
                        no_tasks = int(input("Enter the no. of tasks :- "))
                        for i in range(no_tasks):
                            tasks.append(input("Enter the task :- "))
                            file = open("tasks.txt","a")
                            file.write(f"{i}. {tasks[i]}\n")
                            file.close()
                    elif "no" in query:
                        no_tasks = int(input("Enter the no. of tasks :- "))
                        for i in range(no_tasks):
                            tasks.append(input("Enter the task :- "))
                            file = open("tasks.txt","a")
                            file.write(f"{i}. {tasks[i]}\n")
                            file.close()
                elif "show my schedule" in query:
                    file = open("tasks.txt","r")
                    content = file.read()
                    file.close()
                    mixer.init()
                    mixer.music.load("notification.mp3")
                    mixer.music.play()
                    notification.notify(
                        title = "My schedule :-",
                        message = content,
                        timeout = 15
                    )
                elif "open" in query:   
                    query = query.replace("open","")
                    query = query.replace("Spark","")
                    pyautogui.press("super")
                    pyautogui.typewrite(query)
                    pyautogui.press("enter")
                elif "internet speed" in query:
                    wifi  = speedtest.Speedtest()
                    upload_net = wifi.upload()/1048576         #Megabyte = 1024*1024 Bytes
                    download_net = wifi.download()/1048576
                    print("Wifi Upload Speed is", upload_net)
                    print("Wifi download speed is ", download_net)
                    speak(f"Wifi download speed is {download_net}")
                    speak(f"Wifi upload speed is {upload_net}")
                elif "hello" in query:
                    speak("Hello sir, how are you ?")
                elif "i am fine" in query:
                    speak("that's great, sir")
                elif "how are you" in query:
                    speak("Perfect, sir")
                elif "thank you" in query:
                    speak("you are welcome, sir")
                elif "tired" in query:
                    speak("Playing your favourite songs, sir")
                    a = (1,2,3) # You can choose any number of songs (I have only chosen 3)
                    b = random.choice(a)
                    if b == 1:
                        webbrowser.open("https://www.youtube.com/watch?v=E_SbwSe15y0")
                elif "pause" in query:
                    pyautogui.press("k")
                    speak("video paused")
                elif "play" in query:
                    pyautogui.press("k")
                    speak("video played")
                elif "mute" in query:
                    pyautogui.press("m")
                    speak("video muted")
                elif "volume up" in query:
                    from keyboard import volumeup
                    speak("Turning volume up, sir")
                    volumeup()
                elif "volume down" in query:
                    from keyboard import volumedown
                    speak("Turning volume down, sir")
                    volumedown()
                elif "open" in query:
                    from Dictapp import openappweb
                    openappweb(query)
                elif "close" in query:
                    from Dictapp import closeappweb
                    closeappweb(query)
                elif "google" in query:
                    from SearchNow import searchGoogle
                    searchGoogle(query)
                elif "youtube" in query:
                    from SearchNow import searchYoutube
                    searchYoutube(query)
                elif "wikipedia" in query:
                    from SearchNow import searchWikipedia
                    searchWikipedia(query)
                elif "news" in query:
                    from NewsRead import latestnews
                    latestnews()
                elif "calculate" in query:
                    from Calculatenumbers import WolfRamAlpha
                    from Calculatenumbers import Calc
                    query = query.replace("calculate", "")
                    query = query.replace("Sparkk", "")
                    Calc(query)
                elif "temperature" in query:
                    search = "temperature in Patna"
                    url = f"https://www.google.com/search?q={search}"
                    r  = requests.get(url)
                    data = BeautifulSoup(r.text,"html.parser") 
                    temperature = data.find("div",class_ = "BNeawe").text
                    speak(f"current {search} is {temperature}")
                elif "alarm" in query:
                    speak("Enter the time !")
                    time = input(": Enter the time :")
                    while True:
                        Time_Ac = datetime.datetime.now()
                        now = Time_Ac.strftime("%H:%M:%S")
                        if now == time:
                            speak("Time to wake up sir!")
                            mixer.init()
                            mixer.music.load("alarm.mp3")
                            mixer.music.play()
                        elif now>time:
                            break
                elif "where is" in query:
                    query = query.replace("where is","")
                    location = query
                    speak("User asked to Locate")
                    speak(location)
                    webbrowser.open("https://www.google.nl/maps/place/" + location + "")
                elif "write a note" in query:
                    speak("What should i write, sir")
                    note = takeCommand()
                    file = open('note.txt', 'w')
                    speak("Sir, Should i include date and time")
                    snfm = takeCommand()
                    if 'yes' in snfm or 'sure' in snfm:
                        strTime = datetime.datetime.now().strftime("%H:%M:%S")
                        file.write(strTime)
                        file.write(" :- ")
                        file.write(note)
                    else:
                        file.write(note)
                elif "show note" in query:
                    speak("Showing Notes")
                    file = open("note.txt", "r")
                    print(file.read())
                    speak(file.read())  
                elif "goodbye" in query:
                    speak("Goodbye sir, have a nice day!")
                    exit()

if __name__ == "__main__":
    render_thread = threading.Thread(target=render_thread)
    render_thread.start()

    main_voice_assistant_logic()
