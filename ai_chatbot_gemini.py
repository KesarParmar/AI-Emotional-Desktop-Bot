# ai_chatbot_gemini.py - FIXED VERSION
import speech_recognition as sr
import os
from gtts import gTTS
import google.generativeai as genai

# ⚠️ Replace with your NEW API key
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

# Configure Gemini with updated API
genai.configure(api_key=GEMINI_API_KEY)

# Use latest model (gemini-1.5-flash is free and fast)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Using gemini-1.5-flash model")
except:
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("✅ Using gemini-1.5-pro model")
    except:
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Using gemini-pro model")

# Initialize speech recognizer
recognizer = sr.Recognizer()

def listen():
    """Listen to user's voice and convert to text"""
    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
        print("🤔 Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"👤 You: {text}")
        return text
        
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        print("❌ Couldn't understand audio")
        return "unclear"
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_ai_response(question):
    """Get response from Gemini AI"""
    try:
        # Generate response with proper configuration
        response = model.generate_content(
            f"You are a helpful AI assistant on a Raspberry Pi. Keep responses brief and conversational (2-3 sentences max). User question: {question}",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=150,
                temperature=0.7,
            )
        )
        
        # Check if response has text
        if response.text:
            return response.text
        else:
            return "I'm not sure how to answer that. Could you rephrase?"
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Gemini API Error: {error_msg}")
        
        # Provide helpful error message
        if "404" in error_msg:
            return "My AI model isn't available right now. Please check your API key and internet connection."
        elif "quota" in error_msg.lower():
            return "I've reached my usage limit for now. Please try again later."
        elif "API key" in error_msg:
            return "There's an issue with my API key. Please check the configuration."
        else:
            return "Sorry, I'm having trouble thinking right now."

def speak(text):
    """Convert text to speech via HDMI"""
    print(f"🤖 AI: {text}")
    
    try:
        # Use gTTS for better quality
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save("/tmp/response.mp3")
        
        # Try multiple audio players
        players = ["mpg321 -q", "play -q", "mpg123 -q"]
        for player in players:
            if os.system(f"{player} /tmp/response.mp3 2>/dev/null") == 0:
                break
        
        os.remove("/tmp/response.mp3")
        
    except Exception as e:
        # Fallback to espeak
        text_escaped = text.replace('"', '\\"')
        os.system(f'espeak -s 150 "{text_escaped}"')

def main():
    """Main chatbot loop"""
    print("\n" + "="*60)
    print("🤖 Gemini AI Voice Assistant on Raspberry Pi")
    print("="*60 + "\n")
    
    speak("Hello! I am your Gemini AI assistant. Ask me anything!")
    
    conversation_count = 0
    
    while True:
        # Listen to user
        user_input = listen()
        
        # Handle listening errors
        if user_input is None:
            continue
        if user_input == "unclear":
            speak("Sorry, I didn't catch that. Could you repeat?")
            continue
        
        # Exit conditions
        exit_words = ["goodbye", "exit", "quit", "bye", "stop"]
        if any(word in user_input.lower() for word in exit_words):
            speak("Goodbye! Have a great day!")
            break
        
        # Get AI response
        print("🧠 Thinking...")
        response = get_ai_response(user_input)
        
        # Speak the response
        speak(response)
        
        conversation_count += 1
        
        # Optional: conversation limit
        if conversation_count >= 20:
            speak("We've had a nice long chat! Feel free to start again anytime.")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Chatbot stopped by user")
        os.system('espeak "Chatbot stopped"')
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
