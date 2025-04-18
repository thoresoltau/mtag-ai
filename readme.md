# 🧙‍♂️ MagicCardTagger & Viewer
This project combines Python & React to automatically 
analyze and tag Magic the Gathering cards and display them in a UI.


A combination of information provided at the scryfall.com-API, 
computer vision and natural language processing is used to extract
and combine the data for the cards.

---

## 🔧 Requirements

### 📦 Python (Backend)
- Python 3.9+
- `pip`

### 📦 Node.js & npm (Frontend)
- Node.js >= 18
- npm >= 9

---

## 🐍 Python Part (Tagging & Captioning)

### 🔹 Installation
```bash
pip install transformers torch pillow tqdm requests