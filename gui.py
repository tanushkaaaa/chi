import tkinter as tk  # Explicitly importing tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pyperclip
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator
from constants import themes, tts_langs, languages
from audio import text_to_speech
from translator import manual_translate
from prescription_processor import process_prescription
from googletrans import Translator
import functools
from prescription_processor import get_transliterated_medicines, get_transliterated_medicines



# prescription_processor = {
#     "process_prescription": process_prescription
# }


def create_gui(root, current_theme, history, config, audio, translator, prescription_processor):
    global input_text, translated_text, status_label, progress_bar, volume_scale, save_audio_var, live_translate_var
    global lang_var, theme_var, buttons

    transliterated_medicines = get_transliterated_medicines(config["medicines"])

    # Background Image with Fallback
    try:
        bg_image = Image.open("background.jpg")
        bg_image = bg_image.resize((1000, 700), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo  # Keep reference
    except FileNotFoundError:
        root.configure(bg=themes[current_theme[0]]["bg"])
        bg_label = None

    # Overlay Canvas
    canvas = tk.Canvas(root, bg=themes[current_theme[0]]["bg"] if bg_label is None else "white", highlightthickness=0)
    canvas.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
    if bg_label is not None:
        canvas.create_rectangle(0, 0, 900, 630, fill="#F5F5F5")

    def apply_theme():
        theme = themes[current_theme[0]]
        canvas.configure(bg=theme["bg"])
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground=theme["entry_bg"], background=theme["entry_bg"],
                        foreground=theme["fg"], arrowcolor=theme["fg"])
        style.configure("TFrame", background=theme["frame_bg"])
        style.configure("TProgressbar", troughcolor=theme["frame_bg"], background=theme["accent"])
        
        for widget in root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=theme["frame_bg"])
            elif isinstance(widget, (tk.Label, tk.Button)) and widget != bg_label:
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
        
        for btn in buttons:
            btn.config(bg=theme["btn_bg"], fg=theme["btn_fg"])
        status_label.config(fg=theme["status_fg"])

    def animate_button(button):
        original_bg = button["bg"]
        button.config(bg=themes[current_theme[0]]["accent"])
        root.after(100, lambda: button.config(bg=original_bg))

    def adjust_font_size(increase=True):
        current_size = int(input_text.cget("font").split()[-1])
        new_size = current_size + 1 if increase else current_size - 1
        if 8 <= new_size <= 16:
            input_text.configure(font=("Helvetica", new_size))
            translated_text.configure(font=("Helvetica", new_size))

    def show_history():
        history_window = tk.Toplevel(root)
        history_window.title("Translation History")
        history_window.geometry("600x400")
        history_window.configure(bg=themes[current_theme[0]]["bg"])
        
        text = ScrolledText(history_window, wrap=tk.WORD, height=20, width=70,
                           bg=themes[current_theme[0]]["entry_bg"], fg=themes[current_theme[0]]["fg"])
        text.pack(padx=10, pady=10)
        
        for timestamp, original, translated in history:
            text.insert(tk.END, f"[{timestamp}]\nInput: {original}\nTranslated: {translated}\n\n")
        text.config(state="disabled")

    def edit_medicines(input_text, translated_text, lang, status_label, progress_bar, medicines, history, volume_scale, save_audio_var, root):
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Medicines")
        edit_window.geometry("400x500")
        edit_window.configure(bg=themes[current_theme[0]]["bg"])
        
        listbox = tk.Listbox(edit_window, bg=themes[current_theme[0]]["entry_bg"], 
                            fg=themes[current_theme[0]]["fg"], height=20)
        listbox.pack(padx=10, pady=10, fill="both", expand=True)
        
        for med in config["medicines"]:
            listbox.insert(tk.END, med)
        
        entry = tk.Entry(edit_window, bg=themes[current_theme[0]]["entry_bg"], 
                        fg=themes[current_theme[0]]["fg"])
        entry.pack(pady=5)
        
        def add_medicine():
            med = entry.get().strip()
            if med and med not in config["medicines"]:
                config["medicines"].append(med)
                listbox.insert(tk.END, med)
                config["save_medicines"](config["medicines"])
                entry.delete(0, tk.END)
        
        def remove_medicine():
            try:
                idx = listbox.curselection()[0]
                config["medicines"].pop(idx)
                listbox.delete(idx)
                config["save_medicines"](config["medicines"])
            except:
                pass
        
        tk.Button(edit_window, text="➕ Add", command=add_medicine,
                 bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"]).pack(pady=5)
        tk.Button(edit_window, text="➖ Remove", command=remove_medicine,
                 bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"]).pack(pady=5)

    def show_help():
        messagebox.showinfo("Help", """
        Speech & Text Translator Help
        - 🎤 Speech to Text: Convert speech to text (Ctrl+S)
        - 🌐 Translate: Translate input text (Ctrl+T)
        - 💊 Prescription: Process medical prescriptions (Ctrl+P)
        - 🗑 Clear: Clear text areas (Ctrl+R)
        - 🔊 Language: Play translated text as audio
        - 📜 History: View past translations (Ctrl+H)
        - ⚙ Edit Medicines: Modify medicine list
        - 🔍+/-: Adjust font size
        - 📥/📋: Copy/paste text
        - ☑ Live Translate: Enable real-time translation
        - 💾 Save Audio: Save TTS audio
        - Theme: Change color scheme
        - Volume: Adjust TTS volume
        """)

    def clear_text():
        input_text.delete("1.0", tk.END)
        translated_text.delete("1.0", tk.END)
        status_label.config(text="🗑 Cleared")

    # GUI Layout
    header_frame = tk.Frame(canvas, bg=themes[current_theme[0]]["frame_bg"])
    header_frame.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.1)
    title = tk.Label(header_frame, text="🌍 Speech & Text Translator", 
                    font=("Helvetica", 22, "bold"), bg=themes[current_theme[0]]["frame_bg"], 
                    fg=themes[current_theme[0]]["fg"])
    title.pack(pady=10)

    # Theme and Language Selector
    selector_frame = tk.Frame(canvas, bg=themes[current_theme[0]]["frame_bg"])
    selector_frame.place(relx=0.05, rely=0.12, relwidth=0.9, relheight=0.08)

    theme_label = tk.Label(selector_frame, text="🎨 Theme:", 
                          font=("Helvetica", 12), bg=themes[current_theme[0]]["frame_bg"], 
                          fg=themes[current_theme[0]]["fg"])
    theme_label.pack(side="left", padx=5)
    theme_var = tk.StringVar(value=current_theme[0])
    theme_dropdown = ttk.Combobox(selector_frame, textvariable=theme_var, state="readonly", width=15)
    theme_dropdown['values'] = list(themes.keys())
    theme_dropdown.bind("<<ComboboxSelected>>", lambda e: [current_theme.__setitem__(0, theme_var.get()), config["save_theme"](current_theme[0]), apply_theme()])
    theme_dropdown.pack(side="left", padx=10)

    lang_label = tk.Label(selector_frame, text="🌐 Language:", 
                         font=("Helvetica", 12), bg=themes[current_theme[0]]["frame_bg"], 
                         fg=themes[current_theme[0]]["fg"])
    lang_label.pack(side="left", padx=5)
    lang_var = tk.StringVar()
    language_dropdown = ttk.Combobox(selector_frame, textvariable=lang_var, state="readonly", width=20)
    language_dropdown['values'] = languages
    language_dropdown.current(0)
    language_dropdown.pack(side="left", padx=10)

    # Main Content
    paned_window = tk.PanedWindow(canvas, orient=tk.HORIZONTAL, bg=themes[current_theme[0]]["bg"])
    paned_window.place(relx=0.05, rely=0.22, relwidth=0.9, relheight=0.4)

    input_frame = tk.LabelFrame(paned_window, text="Input Text / Speech", 
                               font=("Helvetica", 12), bg=themes[current_theme[0]]["frame_bg"], 
                               fg=themes[current_theme[0]]["fg"], bd=2, relief="groove")
    paned_window.add(input_frame)
    paned_window.paneconfigure(input_frame, stretch="always")

    input_text = tk.Text(input_frame, height=8, width=40, wrap=tk.WORD, 
                        font=("Helvetica", 10), undo=True)
    input_text.pack(padx=10, pady=10)

    input_btn_frame = tk.Frame(input_frame, bg=themes[current_theme[0]]["frame_bg"])
    input_btn_frame.pack(fill="x", padx=10, pady=5)
    tk.Button(input_btn_frame, text="📥 Paste", 
             command=lambda: input_text.insert("end", pyperclip.paste()),
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Button(input_btn_frame, text="📋 Copy", 
             command=lambda: pyperclip.copy(input_text.get("1.0", "end-1c")),
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Button(input_btn_frame, text="↩ Undo", 
             command=input_text.edit_undo,
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Button(input_btn_frame, text="↪ Redo", 
             command=input_text.edit_redo,
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)

    output_frame = tk.LabelFrame(paned_window, text="Translated Text / Speech", 
                               font=("Helvetica", 12), bg=themes[current_theme[0]]["frame_bg"], 
                               fg=themes[current_theme[0]]["fg"], bd=2, relief="groove")
    paned_window.add(output_frame)
    paned_window.paneconfigure(output_frame, stretch="always")

    translated_text = tk.Text(output_frame, height=8, width=40, wrap=tk.WORD, 
                            font=("Helvetica", 10), undo=True)
    translated_text.pack(padx=10, pady=10)

    output_btn_frame = tk.Frame(output_frame, bg=themes[current_theme[0]]["frame_bg"])
    output_btn_frame.pack(fill="x", padx=10, pady=5)
    tk.Button(output_btn_frame, text="📋 Copy", 
             command=lambda: pyperclip.copy(translated_text.get("1.0", "end-1c")),
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Button(output_btn_frame, text="↩ Undo", 
             command=translated_text.edit_undo,
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)
    tk.Button(output_btn_frame, text="↪ Redo", 
             command=translated_text.edit_redo,
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=8, font=("Helvetica", 10)).pack(side="left", padx=5)

    font_frame = tk.Frame(canvas, bg=themes[current_theme[0]]["bg"])
    font_frame.place(relx=0.05, rely=0.62, relwidth=0.9, relheight=0.05)
    tk.Button(font_frame, text="🔍+", command=lambda: adjust_font_size(True),
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=5).pack(side="left", padx=5)
    tk.Button(font_frame, text="🔍−", command=lambda: adjust_font_size(False),
             bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"], 
             width=5).pack(side="left", padx=5)
    save_audio_var = tk.BooleanVar()
    tk.Checkbutton(font_frame, text="💾 Save Audio", variable=save_audio_var,
                  bg=themes[current_theme[0]]["bg"], fg=themes[current_theme[0]]["fg"]).pack(side="left", padx=10)
    live_translate_var = tk.BooleanVar()
    live_check = tk.Checkbutton(font_frame, text="☑ Live Translate", variable=live_translate_var,
                              bg=themes[current_theme[0]]["bg"], fg=themes[current_theme[0]]["fg"])
    live_check.pack(side="left", padx=10)

    button_frame = tk.Frame(canvas, bg=themes[current_theme[0]]["bg"])
    button_frame.place(relx=0.05, rely=0.67, relwidth=0.9, relheight=0.08)
    buttons = []

    btn_configs = [
    ("🎤 Speech to Text", lambda: audio["speech_to_text"](status_label, progress_bar, input_text, translated_text, lang_var.get().split()[-1], history, GoogleTranslator)),
    ("🌐 Translate", lambda: translator["manual_translate"](input_text, translated_text, lang_var.get().split()[-1], status_label, history, GoogleTranslator)),
    ("💊 Prescription", lambda: prescription_processor["process_prescription"](
        input_text, 
        translated_text, 
        lang_var.get(), 
        lang_var.get().split()[-1], 
        status_label, 
        progress_bar, 
        config["medicines"], 
        prescription_processor["transliterated_medicines"],  # Get it from the dictionary
        history, 
        volume_scale, 
        save_audio_var, 
        root)),
    ("🗑 Clear", clear_text),
    ("📜 History", show_history),
    ("⚙ Medicines", lambda: edit_medicines(input_text, translated_text, lang_var.get().split()[-1], status_label, progress_bar, config["medicines"], history, volume_scale, save_audio_var, root)),
    ("❓ Help", show_help)
]

    for idx, (text, cmd) in enumerate(btn_configs):
        btn = tk.Button(button_frame, text=text, 
               width=12, font=("Helvetica", 10, "bold"), 
               bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"],
               relief="raised", bd=3, command=cmd)
    
        btn.grid(row=0, column=idx, padx=10, pady=5)
        buttons.append(btn)




    tts_frame = tk.LabelFrame(canvas, text="Text to Speech", font=("Helvetica", 12),
                             bg=themes[current_theme[0]]["frame_bg"], fg=themes[current_theme[0]]["fg"],
                             bd=2, relief="groove")
    tts_frame.place(relx=0.05, rely=0.75, relwidth=0.9, relheight=0.12)

    for idx, (label, code) in enumerate(tts_langs.items()):
        btn = tk.Button(tts_frame, text=label, 
                       command=lambda c=code: [audio["text_to_speech"](c, translated_text, status_label, progress_bar, volume_scale, save_audio_var, root), animate_button(btn)], 
                       width=12, font=("Helvetica", 10),
                       bg=themes[current_theme[0]]["btn_bg"], fg=themes[current_theme[0]]["btn_fg"],
                       relief="raised", bd=3)
        btn.grid(row=0, column=idx, padx=5, pady=10)
        buttons.append(btn)

    volume_label = tk.Label(tts_frame, text="🔊 Volume:", bg=themes[current_theme[0]]["frame_bg"],
                           fg=themes[current_theme[0]]["fg"], font=("Helvetica", 10))
    volume_label.grid(row=1, column=0, padx=5, pady=5)
    volume_scale = tk.Scale(tts_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, resolution=0.1,
                           bg=themes[current_theme[0]]["frame_bg"], fg=themes[current_theme[0]]["fg"],
                           highlightthickness=0)
    volume_scale.set(0.8)
    volume_scale.grid(row=1, column=1, columnspan=5, sticky="ew", padx=5)

    progress_bar = ttk.Progressbar(canvas, maximum=100, style="TProgressbar")
    progress_bar.place(relx=0.05, rely=0.87, relwidth=0.9, relheight=0.03)
    status_label = tk.Label(canvas, text="Ready", font=("Helvetica", 10, "italic"),
                           bg=themes[current_theme[0]]["bg"], fg=themes[current_theme[0]]["status_fg"])
    status_label.place(relx=0.05, rely=0.90, relwidth=0.9, relheight=0.05)

    def on_key_release(event):
        if live_translate_var.get():
            translator["manual_translate"](input_text, translated_text, lang_var.get().split()[-1], status_label, history, GoogleTranslator)

    input_text.bind("<KeyRelease>", on_key_release)

    root.bind('<Control-s>', lambda e: [audio["speech_to_text"](status_label, progress_bar, input_text, translated_text, lang_var.get().split()[-1], history, GoogleTranslator), animate_button(buttons[0])])
    root.bind('<Control-t>', lambda e: [translator["manual_translate"](input_text, translated_text, lang_var.get().split()[-1], status_label, history, GoogleTranslator), animate_button(buttons[1])])
    root.bind('<Control-p>', lambda e: [prescription_processor["process_prescription"](input_text, translated_text, lang_var.get().split()[-1], status_label, progress_bar, config["medicines"], history, volume_scale, save_audio_var, root, GoogleTranslator), animate_button(buttons[2])])
    root.bind('<Control-r>', lambda e: [clear_text(), animate_button(buttons[3])])
    root.bind('<Control-h>', lambda e: [show_history(), animate_button(buttons[4])])

    apply_theme()

    return {
        "input_text": input_text,
        "translated_text": translated_text,
        "status_label": status_label,
        "progress_bar": progress_bar,
        "volume_scale": volume_scale,
        "save_audio_var": save_audio_var,
        "live_translate_var": live_translate_var,
        "lang_var": lang_var,
        "theme_var": theme_var
    }