import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"
import easyocr

print("Initializing EasyOCR reader...")
reader = easyocr.Reader(['en'], gpu=False, verbose=False)
print("EasyOCR reader initialized successfully.")

# Test on clean passport
res = reader.readtext('backend/static/documents/passport_arthur_clean.jpg')
for bbox, text, conf in res:
    if conf > 0.3:
        print(f"  Detected: '{text}' (confidence: {conf:.2f})")
