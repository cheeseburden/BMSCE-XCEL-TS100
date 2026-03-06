# 🔍 AI Code Review Assistant

An intelligent, AI-powered code review tool built with **Python**, **LangChain**, **Groq** (free tier), and **Streamlit**.

---

## 🚀 Setup Guide

### Option A: Run with Docker (Recommended)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd "Code Crusaders"
```

2. **Build and Run:**
```bash
# Build the Docker image
docker build -t code-crusaders .

# Run the container (with persistent database volume)
docker run -p 8501:8501 -v code-crusaders-data:/app/data code-crusaders
```
The app will be available at [http://localhost:8501](http://localhost:8501).

---

### Option B: Run Locally

1. **Clone the repository:**
```bash
git clone <repository-url>
cd "Code Crusaders"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run app.py
```

---

## 🔑 Getting Started

1. Open the app at `http://localhost:8501`
2. Get a **FREE** Groq API key from [console.groq.com](https://console.groq.com/keys)
3. Paste your API key in the app's sidebar
4. Paste your code, upload a file, or fetch a GitHub URL
5. Click **"🚀 Run AI Code Review"**
