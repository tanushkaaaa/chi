import tkinter as tk
from gui import create_gui
from config import load_theme, save_theme, load_medicines, save_medicines
from audio import speech_to_text, text_to_speech
from translator import manual_translate
from prescription_processor import process_prescription, get_transliterated_medicines

def main():
    root = tk.Tk()
    root.title("🌍 Speech & Text Translator")
    root.geometry("1000x700")
    root.resizable(False, False)

    current_theme = [load_theme()]  # Mutable list to allow GUI updates
    config = {
        "load_theme": load_theme,
        "save_theme": save_theme,
        "medicines": load_medicines(),
        "save_medicines": save_medicines
    }
    audio = {
        "speech_to_text": speech_to_text,
        "text_to_speech": text_to_speech
    }
    translator = {
        "manual_translate": manual_translate
    }
    
    # Calculate transliterated_medicines here where config is available
    transliterated_medicines = get_transliterated_medicines(config["medicines"])
    
    prescription_processor = {
        "process_prescription": process_prescription,
        "transliterated_medicines": transliterated_medicines  # Pass it through the dictionary
    }
    history = []

    gui = create_gui(root, current_theme, history, config, audio, translator, prescription_processor)

    root.mainloop()

if __name__ == "__main__":
    main()