import pyttsx3

word = input("Enter word to pronounce: ")

engine = pyttsx3.init()
engine.say(word)
engine.runAndWait()
