# === Camera + TFT Setup ===
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.ili9341 as ili9341
from tensorflow.keras.models import load_model

# --- SPI TFT Setup (FIXED TO MATCH YOUR WORKING CODE) ---
# Using the pins that work for your TFT test
cs_pin = digitalio.DigitalInOut(board.CE0)     # Changed from D8 to CE0
dc_pin = digitalio.DigitalInOut(board.D25)     # Changed from D24 to D25  
reset_pin = digitalio.DigitalInOut(board.D24)  # Changed from D25 to D24

# Use board.SPI() instead of busio.SPI() to match working code
spi = board.SPI()
disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=24000000)

print("✅ TFT Display initialized with correct pins")

# --- TFT Canvas Setup ---
width = disp.height   # 320
height = disp.width   # 240
image = Image.new("RGB", (height, width))
draw = ImageDraw.Draw(image)
eye_color = (0, 255, 255)
bg_color = (0, 0, 0)

# --- Eye Drawing Utilities ---
def draw_eye_rect(x, y, w, h, r=9):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=eye_color)

def show_on_tft():
    try:
        rotated = image.rotate(90, expand=False)
        disp.image(rotated)
    except Exception as e:
        print(f"Display error: {e}")

def clear():
    draw.rectangle((0, 0, width, height), fill=bg_color)

# --- EMO Reactions ---
def draw_happy():
    print("Drawing HAPPY face...")
    clear()
    draw.line([(35, 130), (70, 95)], fill=eye_color, width=10)
    draw.line([(65, 95), (95, 130)], fill=eye_color, width=10)
    draw.line([(145, 130), (180, 95)], fill=eye_color, width=10)
    draw.line([(175, 95), (205, 130)], fill=eye_color, width=10)
    show_on_tft()

def draw_sad():
    print("Drawing SAD face...")
    clear()
    draw.line([(35, 110), (70, 135)], fill=eye_color, width=10)
    draw.line([(65, 135), (95, 110)], fill=eye_color, width=10)
    draw.line([(145, 110), (180, 135)], fill=eye_color, width=10)
    draw.line([(175, 135), (205, 110)], fill=eye_color, width=10)
    show_on_tft()

def draw_angry():
    print("Drawing ANGRY face...")
    clear()
    draw.line([(35, 100), (100, 120)], fill=eye_color, width=6)
    draw.line([(35, 120), (100, 140)], fill=eye_color, width=11)
    draw.line([(145, 120), (210, 100)], fill=eye_color, width=6)
    draw.line([(145, 140), (210, 120)], fill=eye_color, width=11)
    show_on_tft()

def draw_neutral():
    print("Drawing NEUTRAL face...")
    clear()
    draw_eye_rect(40, 100, 60, 70)
    draw_eye_rect(160, 100, 60, 70)
    show_on_tft()

# --- Emotion Handling ---
def show_emotion_on_display(emotion):
    print(f"🎭 Detected: {emotion}")
    try:
        if emotion == "Happy":
            draw_happy()
        elif emotion == "Sad":
            draw_sad()
        elif emotion == "Angry":
            draw_angry()
        else:
            draw_neutral()
        print(f"✅ {emotion} face displayed")
    except Exception as e:
        print(f"❌ Error showing {emotion}: {e}")

# Test the display first with a startup pattern
print("Testing display with startup pattern...")
try:
    # Quick test - flash different colors like your working code
    colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,255)]
    for color in colors:
        test_image = Image.new("RGB", (height, width), color)
        disp.image(test_image.rotate(90, expand=False))
        time.sleep(0.5)
    
    # Show neutral face as default
    draw_neutral()
    print("✅ Display test complete - showing neutral face")
    
except Exception as e:
    print(f"❌ Display test failed: {e}")
    exit(1)

# --- Load Emotion Model ---
try:
    print("Loading emotion model...")
    emotion_model = load_model("emotion_model.hdf5", compile=False)
    emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
    print("✅ Emotion model loaded")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    exit(1)

# --- Init Camera ---
try:
    print("Initializing camera...")
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (320, 240)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2)
    print("✅ Camera initialized")
except Exception as e:
    print(f"❌ Camera failed: {e}")
    exit(1)

# Initialize face cascade
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("✅ Face detection ready")
except Exception as e:
    print(f"❌ Face cascade failed: {e}")
    exit(1)

print("\n🚀 Starting emotion detection...")
print("Look at the camera to see your emotions!")

# --- Main Loop ---
prev_emotion = None
frame_count = 0

try:
    while True:
        frame_count += 1
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (64, 64))
                face = face.astype("float32") / 255.0
                face = np.expand_dims(face, axis=0)
                face = np.expand_dims(face, axis=-1)
                
                prediction = emotion_model.predict(face, verbose=0)
                emotion = emotion_labels[np.argmax(prediction)]
                confidence = np.max(prediction)
                
                if emotion != prev_emotion and confidence > 0.4:
                    print(f"\nFrame {frame_count}: {emotion} (confidence: {confidence:.2f})")
                    show_emotion_on_display(emotion)
                    prev_emotion = emotion
                
                break  # Only show 1 face's emotion
        else:
            # No face detected - show neutral if not already
            if prev_emotion != "Neutral":
                show_emotion_on_display("Neutral")
                prev_emotion = "Neutral"
        
        time.sleep(0.8)  # Reasonable delay
        
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
    
except Exception as e:
    print(f"❌ Error in main loop: {e}")
    
finally:
    try:
        picam2.stop()
        # Clear display
        clear()
        show_on_tft()
        print("✅ Cleanup complete")
    except:
        pass
