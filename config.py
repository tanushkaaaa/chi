import json
import os

CONFIG_FILE = "theme_config.json"
MEDICINES_FILE = "medicines.json"

def load_theme():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("theme", "soothing")
    return "soothing"

def save_theme(theme):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"theme": theme}, f)

def load_medicines():
    if os.path.exists(MEDICINES_FILE):
        with open(MEDICINES_FILE, "r") as f:
            return json.load(f)
    return [
        "Paracetamol", "Combiflam", "Amoxicillin", "Cefixime", "Azithromycin",
        "Cetirizine", "Montair-LC", "Pantoprazole", "Pan-D", "Metformin",
        "Losartan", "Telmisartan", "Amlodipine", "Asthalin Inhaler", "Becosules"
    ]

def save_medicines(medicines):
    with open(MEDICINES_FILE, "w") as f:
        json.dump(medicines, f)