# 🐰 Talking Rabbitt

> **When your data finally learns to talk back...**

An AI-powered multi-agent data analytics dashboard that transforms raw CSV/Excel files into interactive insights through natural language conversation. Upload your data, ask questions with your voice, and get intelligent visualizations instantly.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge)](https://talking-rabbitt.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

### 🧹 **Automated Data Cleaning**
- Detects and fills missing values (mean for numeric, mode for categorical)
- Removes duplicate rows automatically
- Converts date columns intelligently

### 📊 **Intelligent Multi-Chart Dashboard**
- Generates **4+ contextually relevant visualizations** based on your data
- Interactive Plotly charts with hover effects
- Smart chart selection (line charts for trends, bar charts for categories, etc.)

### 🎤 **Voice-Enabled Q&A**
- Ask questions using voice or text input
- Get **automatic voice responses** (no play button needed!)
- View the exact Python/Pandas code behind every answer

### 🎨 **Premium UI/UX**
- Glassmorphism design with dark mode aesthetics
- Responsive grid layout for visualizations
- Custom CSS with Google Fonts (Outfit)

---

## 🏗️ Architecture

Talking Rabbitt uses a **multi-agent system** powered by Groq Cloud LLM:

```
┌─────────────────────────────────────────────────┐
│           User Uploads CSV/Excel                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         🧹 AGENT 1: Data Janitor
         (Cleans & Prepares Data)
                 │
                 ▼
         🎨 AGENT 2: Viz Architect
         (Generates 4 Smart Charts)
                 │
                 ▼
         🐰 AGENT 3: Talking Rabbitt
         (Answers Your Questions)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Groq API Key ([Get one here](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/talking-rabbitt.git
cd talking-rabbitt
```

2. **Create a virtual environment**
```bash
python -m venv my_env
source my_env/bin/activate  # On Windows: my_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add your Groq API Key**
   
   Open `app.py` and replace the API key on line 15:
   ```python
   API_KEY = "your_groq_api_key_here"
   ```
   
   **For production**, use Streamlit secrets:
   ```bash
   mkdir .streamlit
   echo 'GROQ_API_KEY = "your_key_here"' > .streamlit/secrets.toml
   ```

5. **Run the app**
```bash
streamlit run app.py
```

6. **Open your browser**
   
   Navigate to `http://localhost:8501`

---

## 📖 Usage

### 1️⃣ Upload Your Data
- Click **"Upload Excel or CSV"** in the sidebar
- Supports `.csv` and `.xlsx` files
- Data is automatically cleaned upon upload

### 2️⃣ Generate Visualizations
- Click **"Generate Dashboard Analysis"**
- Wait for the AI to analyze your data
- View 4 intelligent charts in a 2x2 grid

### 3️⃣ Ask Questions
**Text Input:**
- Type your question: *"What is the total revenue?"*
- Get instant text answer + code logic

**Voice Input:**
- Click 🎤 **Speak** button
- Ask your question verbally
- Get **automatic voice response** + text + code

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit, Custom CSS (Glassmorphism) |
| **Visualizations** | Plotly Express |
| **LLM Provider** | Groq Cloud (moonshotai/kimi-k2-instruct-0905) |
| **Data Processing** | Pandas |
| **Voice Input** | streamlit-mic-recorder |
| **Voice Output** | gTTS (Google Text-to-Speech) |
| **Language** | Python 3.10+ |

---

## 📂 Project Structure

```
talking-rabbitt/
│
├── app.py                 # Main Streamlit application
├── agents.py              # Multi-agent logic (Janitor, Viz Architect, Talking Rabbitt)
├── utils.py               # CSS injection & UI helpers
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🤖 How It Works

### Agent 1: Data Janitor
- **Input:** Raw DataFrame
- **Process:** Rule-based cleaning (no LLM)
- **Output:** Clean DataFrame with filled NAs, no duplicates

### Agent 2: Viz Architect
- **Input:** Clean DataFrame + metadata
- **Process:** LLM analyzes columns and generates Plotly code
- **Output:** 4 charts with "story" headlines

### Agent 3: Talking Rabbitt
- **Input:** User question (voice/text)
- **Process:** 
  1. LLM converts question → Pandas query
  2. Execute query on DataFrame
  3. LLM synthesizes natural language answer
  4. gTTS generates voice (if voice input)
- **Output:** Answer (text + voice) + code

---

## 🎯 Use Cases

### Business Analytics
- Upload sales data → Ask: *"Which region had the highest growth?"*
- Get: Voice answer + bar chart + Pandas code

### Academic Research
- Upload survey results → Ask: *"What's the average satisfaction score?"*
- Get: Statistical summary + distribution chart

### Financial Analysis
- Upload expense report → Ask: *"Show me spending trends by department"*
- Get: 4 charts (line, pie, bar, box plot)

---

## 🔒 Security Notes

⚠️ **Important:** This project uses `exec()` to run LLM-generated code. While isolated in a namespace, this can be risky in production.

**Recommendations:**
- Use in trusted environments only
- Validate LLM outputs before execution
- Consider sandboxed environments for production
- Never expose API keys in code (use environment variables)

---

## 🐛 Troubleshooting

### Voice Input Not Working
- Ensure browser has microphone permissions
- Use HTTPS or localhost (required for Web Speech API)
- Try Chrome/Firefox (best compatibility)

### Audio Not Autoplaying
- Some browsers block autoplay by default
- User interaction may be required first
- Check browser console for errors

### LLM Errors
- Verify your Groq API key is valid
- Check internet connection
- Ensure you have API credits remaining

---

## 🚧 Future Enhancements

- [ ] Multi-file comparison
- [ ] Export charts as PNG/PDF
- [ ] Database connectivity (SQL, MongoDB)
- [ ] Advanced analytics (regression, clustering)
- [ ] Collaborative dashboards
- [ ] Custom agent creation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq Cloud** for blazing-fast LLM inference
- **Streamlit** for the amazing web framework
- **Plotly** for interactive visualizations
- **Google TTS** for voice synthesis

---

## 📧 Contact

For questions or feedback, reach out:
- **GitHub Issues:** [Report a bug](https://github.com/yourusername/talking-rabbitt/issues)
- **Email:** sandali.srivastava1729@gmail.com

---

<div align="center">

**Made with ❤️ and AI**

⭐ Star this repo if you found it helpful!

</div>
