import speech_recognition as sr
import pygame
from gtts import gTTS
import os
import tempfile
from tkinter import filedialog
import tkinter as tk
import time


def speech_to_text(root,status_label, progress_bar, input_text, translated_text, lang_code, history, GoogleTranslator):
    progress_bar["value"] = 0
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎤 Listening...")
        progress_bar["value"] = 20
        root.update()
        try:
            audio = recognizer.listen(source)
            progress_bar["value"] = 50
            original = recognizer.recognize_google(audio, language='auto')
            progress_bar["value"] = 80
            translated = GoogleTranslator(source='auto', target=lang_code).translate(original)
            input_text.delete("1.0", tk.END)
            input_text.insert("1.0", original)
            translated_text.delete("1.0", tk.END)
            translated_text.insert("1.0", translated)
            status_label.config(text="✅ Translation completed")
            history.append((time.strftime("%Y-%m-%d %H:%M"), original, translated))
            progress_bar["value"] = 100
        except sr.UnknownValueError:
            status_label.config(text="⚠ Couldn't understand audio")
        except Exception as e:
            status_label.config(text=f"❌ Error: {str(e)}")
        progress_bar["value"] = 0

def text_to_speech(lang_code, translated_text, status_label, progress_bar, volume_scale, save_audio_var, root):
    text = translated_text.get("1.0", "end-1c")
    if text.strip():
        progress_bar["value"] = 20
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp_path = tmp.name
            tmp.close()
            tts = gTTS(text=text, lang=lang_code)
            progress_bar["value"] = 50
            tts.save(tmp_path)
            pygame.mixer.init()
            pygame.mixer.music.set_volume(volume_scale.get())
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            progress_bar["value"] = 80
            while pygame.mixer.music.get_busy():
                root.update()
            pygame.mixer.quit()
            if save_audio_var.get():
                save_path = filedialog.asksaveasfilename(defaultextension=".mp3", 
                                                        filetypes=[("MP3 files", "*.mp3")])
                if save_path:
                    os.rename(tmp_path, save_path)
                else:
                    os.remove(tmp_path)
            else:
                os.remove(tmp_path)
            status_label.config(text="🔊 Audio played")
            progress_bar["value"] = 100
        except Exception as e:
            status_label.config(text=f"❌ Error: {str(e)}")
        progress_bar["value"] = 0
    else:
        status_label.config(text="⚠ No text to speak")