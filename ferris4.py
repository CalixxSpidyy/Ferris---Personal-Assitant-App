import speech_recognition as sr
import random
import pyttsx3
import os
import subprocess
from youtube_search import YoutubeSearch
import json
import tkinter as tk
from tkinter import messagebox
import threading
import time
import requests
from datetime import datetime

# Global variables
is_listening = False
listening_thread = None  # Global variable to store the listening thread
stop_event = threading.Event()  # Event to signal the thread to stop

# Greetings function
def greet_user():
    greetings = ["Hello!", "Hi there!", "Greetings!", "Hey!"]
    return random.choice(greetings)

# Function to show the current time
def show_time():
    now = datetime.now()
    return f"The current time is: {now.strftime('%H:%M:%S')}"

# Function to open a website
def open_website():
    import webbrowser
    url = input("Which website would you like to open? ")
    webbrowser.open(url)

# Function to search the web using Google
def search_web(query):
    import webbrowser
    search_url = "https://www.google.com/search?q=" + query
    webbrowser.open(search_url)

# Function to search YouTube for a video
def search_youtube(query):
    import webbrowser
    results = YoutubeSearch(query, max_results=1).to_dict()
    if results:
        video_id = results[0]['id']
        search_url = "https://www.youtube.com/watch?v=" + video_id
        print(search_url)
        webbrowser.open(search_url)
    else:
        speak("Sorry, no results found.")

# Function to fetch a random cool fact
def coolfact():
    limit = 1
    url = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(limit)
    response = requests.get(url, headers={'X-Api-Key': '13o2d2zr/3CD8hXqoD9m2g==wRFUyD2aldohBlul'})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        print("Error:", response.status_code, response.text)
        return "Sorry, there is a problem. Try again later"

# Function to fetch a random quote
def quote():
    api_url = 'https://api.api-ninjas.com/v1/quotes'
    response = requests.get(api_url, headers={'X-Api-Key': '13o2d2zr/3CD8hXqoD9m2g==wRFUyD2aldohBlul'})
    if response.status_code == requests.codes.ok:
        data = response.json()
        quote = data[0]["quote"]
        author = data[0]["author"]
        return f"{quote}... quote from {author}"
    else:
        print("Error:", response.status_code, response.text)
        return "Sorry, there is a problem. Try again later"

# Function to get weather information for a city
def get_weather_info(city):
    api_key = "d90cc6ea97e5f355f8c606672b936e5d"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        data = response.json()
        if data["cod"] == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            weather_info = f"The weather in {city} is {weather_desc}. The temperature is {temp}°C."
            return weather_info
        else:
            return "Sorry, I couldn't retrieve the weather information for that city."
    except Exception as e:
        print(f"An error occurred while fetching weather data: {e}")
        return "Sorry, there was an error while fetching weather information."

# Function to take a note and save it to a file
def take_note():
    speak("Sure, please dictate your note.")
    note_text = listen()
    if note_text:
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        file_path = os.path.join(desktop_path, "notes.txt")
        with open(file_path, "a") as file:
            file.write(note_text + "\n\n")
        print("Note saved successfully on the desktop.")

# Function to open an application
def open_app(app_name):
    try:
        subprocess.Popen(app_name)
    except Exception as e:
        print(f"Error: {e}")

# Function to start a countdown timer
def start_countdown(seconds):
    print(f"Countdown started for {seconds} seconds.")
    time.sleep(seconds)
    print("Time's up! Alarm!")
    speak("Time's up! Alarm!")

# Function to speak text
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to listen to user's speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print("You said:", query)
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
    except sr.RequestError as e:
        print(f"An error occurred while requesting results: {e}")

# Function to process user commands
def process_command(command):
    if "hello" in command:
        speak(greet_user())
    elif "how are you" in command:
        speak("I'm doing great, thank you!")
    elif "what time is it" in command:
        speak(show_time())
    elif "google" in command:
        speak("Ok, searching it now...")
        query_index = command.index("google") + 6
        query = command[query_index:]
        search_web(query)
    elif "youtube" in command:
        speak("Ok, searching it now...")
        query_index = command.index("youtube") + 7
        query = command[query_index:]
        search_youtube(query)
    elif "stop listening" in command:
        stop_listening()
    elif "random fact" in command:
        chat_response = coolfact()
        fact = chat_response.split(':')[1].strip()
        print(fact)
        speak(fact)
    elif "quote" in command:
        chat_response = quote()
        print(chat_response)
        speak(chat_response)
    elif "weather" in command:
        speak("Sure, which city would you like to know the weather forecast for?")
        city = listen()
        if city:
            weather_info = get_weather_info(city)
            speak(weather_info)
    elif "take a note" in command:
        take_note()
    elif "open app" in command:
        speak("Sure, which app you want to open")
        app = listen()
        if app:
            open_app(app)
    elif "countdown" in command:
        try:
            # Extract the number of seconds from the command
            seconds_index = command.index("countdown") + 9
            seconds_str = command[seconds_index:]
            seconds = int(seconds_str)

            if seconds > 0:
                speak(f"Countdown started for {seconds} seconds.")
                countdown_thread = threading.Thread(target=start_countdown, args=(seconds,))
                countdown_thread.start()
            else:
                speak("Sorry, please specify a valid number of seconds for the countdown.")
        except ValueError:
            speak("Sorry, I couldn't understand the duration for the countdown.")
        except Exception as e:
            print(f"Error during countdown: {e}")
    else:
        speak("Sorry, I don't know how to do that yet.")

# Function to continuously listen to user commands
def continuous_listen():
    global is_listening, stop_event
    recognizer = sr.Recognizer()

    while is_listening:
        with sr.Microphone() as source:
            print("Listening...")
            status_label.config(text="Listening...")  # Update status label
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

        if stop_event.is_set():
            break  # Exit the loop if the stop_event is set

        try:
            print("Recognizing...")
            status_label.config(text="Recognizing...")  # Update status label
            query = recognizer.recognize_google(audio)
            print("You said:", query)
            process_command(query.lower())
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print(f"An error occurred while requesting results: {e}")

    # Reset the stop_event when the loop is done
    stop_event.clear()
    status_label.config(text="Idle")

# Function to start listening for user commands
def start_listening():
    global is_listening, listening_thread
    if not is_listening:
        is_listening = True
        status_label.config(text="Listening...")
        listening_thread = threading.Thread(target=continuous_listen)
        listening_thread.start()

# Function to stop listening for user commands
def stop_listening():
    global is_listening, listening_thread
    is_listening = False
    stop_event.set()
    status_label.config(text="Idle")  # Update status label

# Function to handle window close event
def on_close():
    stop_listening()
    root.destroy()

# Function to create a circle in the canvas
def create_circle(canvas, x, y, radius, **kwargs):
    return canvas.create_oval(x - radius, y - radius, x + radius, y + radius, **kwargs, outline='')

# Create the main tkinter window
root = tk.Tk()
root.title("Voice Assistant")
root.protocol("WM_DELETE_WINDOW", on_close)
root.configure(bg="#333")

canvas = tk.Canvas(root, width=300, height=300, bg="#333", highlightthickness=0)
canvas.pack()

# Draw a circle as the background
circle = create_circle(canvas, 150, 150, 140, fill="#444")

listen_button = tk.Button(root, text="On", command=start_listening, bg="#66c2ff", fg="white", font=("Arial", 10), padx=10, bd=0)
stop_button = tk.Button(root, text="Off", command=stop_listening, bg="#ff6666", fg="white", font=("Arial", 10), padx=10, bd=0)

# Use the pack geometry manager for buttons
listen_button.pack(side=tk.LEFT, padx=20, pady=(20, 10))
stop_button.pack(side=tk.RIGHT, padx=20, pady=(20, 10))

# Create a frame to contain the status label and place it in the middle of the circle
status_frame = tk.Frame(canvas, bg="#444", bd=0)
status_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Initial text for status label
status_label = tk.Label(status_frame, text="Idle", bg="#444", fg="white", font=("Arial", 14), pady=5, padx=20)
status_label.pack()

root.mainloop()
