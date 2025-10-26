# 🤖 Gemini AI Voice Assistant (Raspberry Pi)

This project transforms your Raspberry Pi into an intelligent **voice assistant** using the **Gemini AI API**, **SpeechRecognition**, and **Text-to-Speech (gTTS / espeak)**.

### Features
- 🎤 Speech-to-Text (via Google Speech Recognition)
- 🧠 AI Conversation using Gemini API
- 🗣️ Text-to-Speech output
- 🔊 Works with mic + speaker on Raspberry Pi
- 🚀 Modular and expandable

### Installation
Follow the steps in `INSTALL.md` or below summary:

```bash
sudo apt update && sudo apt upgrade -y
pip3 install google-generativeai gtts SpeechRecognition pyaudio
sudo apt install mpg321 espeak -y
python3 ai_chatbot_gemini.py

Security

Create your Gemini API key at https://makersuite.google.com/app/apikey

Store it in an environment variable:

echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc

Author

👤 Developed by KESAR PARMAR
💡 Powered by Raspberry Pi + Gemini AI

