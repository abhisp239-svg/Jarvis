import speech_recognition as sr  # it helps to write only sr instead of long word speech-recognition
import webbrowser
import pyttsx3
import time
import playSong
import threading  # <-- For keeping GUI alive
import tkinter as tk  # <-- For GUI components
import math  # <-- For creating the pulse effect math
import pygame  # <-- For playing custom meme audio files natively

# Initialize speech recognizer
r = sr.Recognizer()

# Initialize pygame audio engine once at startup
pygame.mixer.init()

# A shared global variable to tell our visual effect what the program is doing
current_state = "idle"  # States can be: "idle", "listening", "speaking", "active"

def processCommand(c):
    clist = c.lower().split(" ")
    if(len(clist) == 2 and clist[0] == "open"):
        webbrowser.open(f"https://{clist[1]}.com")
    if(len(clist) == 2 and clist[0] == "play"):
        link = playSong.music[clist[1]]
        webbrowser.open(link)

def speak(text):
    global current_state
    current_state = "speaking"  # <-- TRIGGER EFFECT: Speaking
    
    # CASE 1: Initializing Alexa (Speaks "Yes Initializing Alexa..." + plays custom audio)
    if "Initializing" in text:
        try:
            # Speak the text using the computer TTS voice
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say("Yes " + text)  # Added "Yes" as requested
            engine.runAndWait()
            engine.stop()
            
            # IMMEDIATELY play your custom sound effect after speaking
            # TODO: Replace with your actual initialization audio file path (e.g., sci-fi startup sound)
            pygame.mixer.music.load('IntroName.mp3') 
            pygame.mixer.music.play()
            
            # Wait for the audio file to finish playing before returning to idle
            while pygame.mixer.music.get_busy(): 
                time.sleep(0.05)
                
        except Exception as e:
            print(f"Error during initialization speech/audio sequence: {e}")
        
    # CASE 2: Alexa hears its name (Plays your custom "Yes Sir" meme audio)
    elif text == "Sir":
        try:
            # TODO: Replace with your actual "Yes Sir" audio path
            pygame.mixer.music.load('SamasyaKyaHai.mp3') 
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                time.sleep(0.05)
        except Exception as e:
            print(f"Error playing 'Sir' audio: {e}")

    # CASE 3: No sound detected / Microphone error (Plays your "Error/Fail" meme audio)
    elif text == "not_detected":
        try:
            # TODO: Replace with your actual "Not Detected/Fail" audio path
            pygame.mixer.music.load('errorRecognition.mp3') 
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                time.sleep(0.05)
        except Exception as e:
            print(f"Error playing error audio: {e}")
    
    current_state = "idle"  # <-- TRIGGER EFFECT: Back to normal

# =====================================================================
# BACKGROUND LOGIC LOOP
# =====================================================================
def start_alexa_logic():
    global current_state
    speak("Initializing")
    
    while True:
        print("recognizing...")
        try:
            current_state = "listening"  # <-- TRIGGER EFFECT: Looking for Alexa
            with sr.Microphone() as source:
                print("Listening!...")
                audio = r.listen(source, timeout=5, phrase_time_limit=2)
            
            current_state = "idle"
            word = r.recognize_google(audio)
            
            if(word.lower() == "baburao"):
                speak("Sir")  # <-- Triggers "Yes Sir" meme sound
                
                current_state = "active"  # <-- TRIGGER EFFECT: Waiting for command
                # Listen for command
                with sr.Microphone() as source:
                    print("Alexa Active...")
                    audio = r.listen(source, timeout=20, phrase_time_limit=5)
                    command = r.recognize_google(audio)
                
                processCommand(command)
                    
        except Exception as e:
            current_state = "idle"
            print(f"Something went wrong: {e}")
            
            # TRIGGER EFFECT: Play your "not detected" audio when speech fails or times out
            speak("not_detected") 

# =====================================================================
# THE VISUAL EFFECTS COMPONENT (GUI ADDITION)
# =====================================================================
wave_phase = 0

def draw_visual_effects():
    """An independent background loop that creates visual effects based on current_state"""
    global wave_phase
    canvas.delete("all")
    
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width < 10: width, height = 400, 200 # Default fallback sizes
    mid_y = height // 2
    
    # 1. VISUAL EFFECT: When Alexa is Listening for you
    if current_state == "listening":
        status_label.config(text="Listening...", fg="#00ffcc")
        points = []
        for x in range(0, width, 5):
            y = mid_y + math.sin(x * 0.03 + wave_phase) * 15
            points.append((x, y))
        canvas.create_line(points, fill="#00ffcc", width=3, smooth=True)
        wave_phase += 0.1
        
    # 2. VISUAL EFFECT: When Alexa recognizes its name and wants a command
    elif current_state == "active":
        status_label.config(text="Alexa is Active!", fg="#ff3366")
        points = []
        for x in range(0, width, 5):
            y = mid_y + math.sin(x * 0.08 + wave_phase) * 35 * math.sin(x / width * math.pi)
            points.append((x, y))
        canvas.create_line(points, fill="#ff3366", width=4, smooth=True)
        wave_phase += 0.3

    # 3. VISUAL EFFECT: When the Computer is physically Speaking / Playing Custom Audio
    elif current_state == "speaking":
        status_label.config(text="Speaking...", fg="#ffcc00")
        pulse = abs(math.sin(wave_phase)) * 40
        canvas.create_oval(width//2 - pulse, mid_y - pulse, width//2 + pulse, mid_y + pulse, outline="#ffcc00", width=3)
        wave_phase += 0.15

    # 4. VISUAL EFFECT: When waiting quietly (Idle)
    else:
        status_label.config(text="Sleeping...", fg="#555566")
        canvas.create_line(0, mid_y, width, mid_y, fill="#333344", width=2)
    
    # Run this animation update roughly every 20 milliseconds (~50 FPS)
    root.after(20, draw_visual_effects)

# This launches everything
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Alexa Screen")
    root.geometry("400x350")
    root.configure(bg="#111116")

    # Add a title and descriptive text
    status_label = tk.Label(root, text="Initializing...", font=("Arial", 14, "bold"), bg="#111116", fg="#ffffff")
    status_label.pack(pady=15)

    # The canvas where the visual effects get drawn
    canvas = tk.Canvas(root, bg="#161620", height=200, highlightthickness=0)
    canvas.pack(fill=tk.X, padx=20, pady=10)

    # Start the speech/mic logic loop inside a background thread
    threading.Thread(target=start_alexa_logic, daemon=True).start()

    # Trigger our separate animation timeline
    draw_visual_effects()

    root.mainloop()