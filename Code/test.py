from openai import OpenAI
from gtts import gTTS
import speech_recognition as sr
import time
import pygame

GeminiApiKey = "You_Gemini_Api_Key" # The key is generated here https://aistudio.google.com/apikey

filePathMP3 = "temp.mp3"

client = OpenAI(
    api_key=GeminiApiKey,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Temperature and other model settings
responcesTtemperature = 0.3
maxOutputTokens = 512

userPrompt = "Ви професійний перекладач з мови. Будь ласка не добавляйте власних суджень і сухо перекладайте текст."
text = "Запитайте на яку мову потрібно перекладати і надалі перекладайте на цю мову всі повідомлення."

chatMessages=[{"role": "system", "content": userPrompt}]

language = 'uk' # default Ukrainian language 

# Function to convert microphone to text
def speechToText():
    recognize = sr.Recognizer()
    microphone = sr.Microphone(chunk_size = 2048)

    with microphone as sourceMic:
        recognize.adjust_for_ambient_noise(sourceMic, duration=0.2)

    with microphone as sourceMic:
        audio = recognize.listen(source = sourceMic)

        TextFromAudio = ""

        try:
            TextFromAudio = recognize.recognize_google(audio, language="uk-UA") # Ukrainian voice recognition default
            print(f"> {TextFromAudio}")

        except Exception as e:
            print("Скажіть щось..." + str(e))

    return TextFromAudio

# Play audio file function
def playAudio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()

# Text-to-speech function
def textToSpeech(dataInput: str):
    tts = gTTS(text=dataInput, lang=language)
    tts.save(filePathMP3)
    playAudio(filePathMP3)

# Function to get response from LLM model
def LLMResponce(userText: str):
    new_message = {"role": "user", "content": userText}
    chatMessages.append(new_message)

    output = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=chatMessages,
    temperature=responcesTtemperature,
    max_tokens=maxOutputTokens,
    stream=True
    )

    LLMTextResponce = ""

    for chunk in output:

        delta = chunk.choices[0].delta
        print(delta.content, end="", flush=True)
        LLMTextResponce += str(delta.content)
    
    print()

    textToSpeech(LLMTextResponce)

    new_message = {"role": "assistant", "content": LLMTextResponce}
    chatMessages.append(new_message)

if __name__ == "__main__":
    # Main program cycle
    while True:
        if text != "":
            LLMResponce(text)

        text = speechToText()

        match text: # First command change speaking language in to English
            case "англійська": 
                language = 'en'

        match text: 
            case "французька": 
                language = 'fr'

        match text: 
            case "польська": 
                language = 'pl'
