import time
import tkinter as tk


def manual_translate(input_text, translated_text, lang_code, status_label, history, GoogleTranslator, event=None):
    text = input_text.get("1.0", "end-1c")
    if text.strip():
        try:
            translated = GoogleTranslator(source='auto', target=lang_code).translate(text)
            translated_text.delete("1.0", tk.END)
            translated_text.insert("1.0", translated)
            status_label.config(text="🌐 Text translated")
            if event:
                history.append((time.strftime("%Y-%m-%d %H:%M"), text, translated))
        except Exception as e:
            status_label.config(text=f"❌ Error: {str(e)}")
    else:
        status_label.config(text="⚠ Enter text to translate")