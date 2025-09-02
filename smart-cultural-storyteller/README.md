# 🌍 Smart Cultural Storyteller

Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨ — powered by [OpenRouter](https://openrouter.ai).

## Features
- 🎭 Choose from Folk Tales, Historical Events, or Traditions
- 🌓 Light/Dark theme toggle
- 📥 Download generated stories
- 📜 Persistent story preview

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-cultural-storyteller.git
cd smart-cultural-storyteller
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Create a `.streamlit/secrets.toml` file:
```toml
OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

### 4. Run the app locally
```bash
streamlit run app.py
```

---

## 🚀 Deploy to Streamlit Cloud

1. Push this folder to a public GitHub repo  
2. Go to [Streamlit Cloud](https://share.streamlit.io)  
3. Connect your repo → select `app.py`  
4. Add the secret `OPENROUTER_API_KEY` in **Streamlit → Settings → Secrets**  

You're ready to go! 🎉

---

## 📦 Git commands to push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Smart Cultural Storyteller"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smart-cultural-storyteller.git
git push -u origin main
```
