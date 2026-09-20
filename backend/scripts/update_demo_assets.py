import os
import io
from PIL import Image, ImageDraw

ARTIFACT_DIR = r"C:\Users\kpaha\.gemini\antigravity-ide\brain\2185d235-8d8b-4af8-bea0-d971b4ab0cd9"
DOCS_DIR = os.path.join("backend", "static", "documents")
FACES_DIR = os.path.join("backend", "static", "faces")

def update_assets():
    # 1. Arthur Pendelton
    p_arthur = Image.open(os.path.join(ARTIFACT_DIR, "arthur_portrait_1789639187083.jpg")).convert("RGB")
    l_arthur = Image.open(os.path.join(ARTIFACT_DIR, "arthur_live_1789639403334.jpg")).convert("RGB")

    doc_arthur = Image.open(os.path.join(DOCS_DIR, "passport_arthur_clean.jpg")).convert("RGB")
    doc_arthur.paste(p_arthur.resize((180, 230)), (40, 90))
    doc_arthur.save(os.path.join(DOCS_DIR, "passport_arthur_clean.jpg"), quality=95)
    l_arthur.save(os.path.join(FACES_DIR, "live_arthur.jpg"), quality=95)
    print("Updated Arthur Pendelton assets (Clean scenario)")

    # 2. Marcus Vance (Tampered Document)
    p_marcus = Image.open(os.path.join(ARTIFACT_DIR, "marcus_portrait_1789639992864.jpg")).convert("RGB")
    l_marcus = Image.open(os.path.join(ARTIFACT_DIR, "marcus_live_1789640048229.jpg")).convert("RGB")

    doc_marcus = Image.open(os.path.join(DOCS_DIR, "passport_marcus_tampered.jpg")).convert("RGB")
    doc_marcus.paste(p_marcus.resize((180, 230)), (40, 90))

    # Add real quantization mismatched altered patch for expiration date
    patch = Image.new("RGB", (230, 32), (255, 255, 235))
    d = ImageDraw.Draw(patch)
    d.rectangle([(0, 0), (229, 31)], outline=(210, 200, 160))
    d.text((8, 8), "28/12/2032 [ALTERED]", fill=(15, 15, 15))
    buf = io.BytesIO()
    patch.save(buf, "JPEG", quality=20)
    buf.seek(0)
    spliced = Image.open(buf)
    doc_marcus.paste(spliced, (246, 362))

    # Genuine EXIF software tag
    exif = doc_marcus.getexif()
    exif[0x0131] = "Adobe Photoshop 2024 (Windows)"
    doc_marcus.save(os.path.join(DOCS_DIR, "passport_marcus_tampered.jpg"), quality=95, exif=exif)
    l_marcus.save(os.path.join(FACES_DIR, "live_marcus.jpg"), quality=95)
    print("Updated Marcus Vance assets (Tampered scenario)")

    # 3. Elena Vance / Elena Rostova (Identity Fracture)
    p_elena = Image.open(os.path.join(ARTIFACT_DIR, "elena_portrait_1789640090957.jpg")).convert("RGB")
    l_elena = Image.open(os.path.join(ARTIFACT_DIR, "elena_live_1789640144707.jpg")).convert("RGB")

    doc_elena_usa = Image.open(os.path.join(DOCS_DIR, "passport_elena_fracture_usa.jpg")).convert("RGB")
    doc_elena_usa.paste(p_elena.resize((180, 230)), (40, 90))
    doc_elena_usa.save(os.path.join(DOCS_DIR, "passport_elena_fracture_usa.jpg"), quality=95)

    doc_elena_rus = Image.open(os.path.join(DOCS_DIR, "passport_elena_historical_rus.jpg")).convert("RGB")
    doc_elena_rus.paste(p_elena.resize((180, 230)), (40, 90))
    doc_elena_rus.save(os.path.join(DOCS_DIR, "passport_elena_historical_rus.jpg"), quality=95)

    l_elena.save(os.path.join(FACES_DIR, "live_elena_shared.jpg"), quality=95)
    print("Updated Elena Vance / Elena Rostova assets (Identity Fracture scenario)")

if __name__ == "__main__":
    update_assets()
