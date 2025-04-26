import speech_recognition as sr
import pygame
from gtts import gTTS
import os
import tempfile
from tkinter import filedialog
import time
import tkinter as tk
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI
import json
import os
from googletrans import Translator

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import unicodedata


# Function to load medicines from the JSON file
def load_medicines():
    if os.path.exists(MEDICINES_FILE):
        with open(MEDICINES_FILE, "r") as f:
            return json.load(f)
    else:
        # Return a default list of medicines if the file doesn't exist
        return [
            "Paracetamol", "Combiflam", "Amoxicillin", "Cefixime", "Azithromycin",
            "Cetirizine", "Montair-LC", "Pantoprazole", "Pan-D", "Metformin",
            "Losartan", "Telmisartan", "Amlodipine", "Asthalin Inhaler", "Becosules"
        ]

MEDICINES_FILE = "medicines.json"

# Initialize transliterated medicines list
def get_transliterated_medicines(medicines):
    return [transliterate(med, ITRANS, DEVANAGARI) for med in medicines]

# Loading medicines and getting transliterated versions
medicines = load_medicines()  # Assume this loads the list of medicines
transliterated_medicines = get_transliterated_medicines(medicines)


def get_script_code(lang_code):
    # Map of language codes to script codes in the indic_transliteration library
    script_map = {
        'hi': sanscript.DEVANAGARI,  # Hindi
        'bn': sanscript.BENGALI,     # Bengali
        'ta': sanscript.TAMIL,       # Tamil
        'te': sanscript.TELUGU,      # Telugu
        'kn': sanscript.KANNADA,     # Kannada
        'ml': sanscript.MALAYALAM,   # Malayalam
        'gu': sanscript.GUJARATI,    # Gujarati
        'or': sanscript.ORIYA,       # Oriya
        'pa': sanscript.GURMUKHI,    # Punjabi
    }
    return script_map.get(lang_code, None)  # Return None if language not supported

# Function to transliterate a medicine name to the target script
def transliterate_to_script(text, lang_code):
    script = get_script_code(lang_code)
    if script:
        try:
            # Try to transliterate from Latin to the target script
            return transliterate(text, sanscript.ITRANS, script)
        except:
            # Return original if transliteration fails
            return text
    else:
        # For unsupported scripts, just return the original text
        return text

def process_prescription(input_text, translated_text, lang, lang_code, status_label, progress_bar, medicines, transliterated_medicines, history, volume_scale, save_audio_var, root):
    progress_bar["value"] = 0
    input_source = input_text.get("1.0", "end-1c").strip()

    if not input_source:
        # Speech recognition code here (unchanged)
        # ...
        pass

    if not input_source:
        status_label.config(text="⚠ Provide a prescription")
        return

    status_label.config(text="📝 Processing prescription...")
    progress_bar["value"] = 60
    root.update_idletasks()

    try:
        translator = Translator()
        words = input_source.split()
        translated_words = []
        current_phrase = []

        for word in words:
            is_medicine = False
            for med in medicines:
                if word.lower() == med.lower():
                    # Transliterate the medicine name to the target script based on lang_code
                    transliterated_med = transliterate_to_script(med, lang_code)
                    translated_words.append(transliterated_med)
                    is_medicine = True
                    break
            if not is_medicine:
                current_phrase.append(word)
            else:
                if current_phrase:
                    phrase = " ".join(current_phrase)
                    translated_phrase = translator.translate(phrase, src='auto', dest=lang_code).text
                    translated_words.append(translated_phrase)
                    current_phrase = []

        if current_phrase:
            phrase = " ".join(current_phrase)
            translated_phrase = translator.translate(phrase, src='auto', dest=lang_code).text
            translated_words.append(translated_phrase)

        translated_prescription = " ".join(translated_words)
        translated_text.delete("1.0", tk.END)
        translated_text.insert("1.0", translated_prescription)
        status_label.config(text="✅ Prescription processed")
        history.append((time.strftime("%Y-%m-%d %H:%M"), input_source, translated_prescription))
        progress_bar["value"] = 80

        # TTS code here (unchanged)
        # ...
        
    except Exception as e:
        status_label.config(text=f"❌ Error: {str(e)}")
        progress_bar["value"] = 0