# 📄 Resume Critic Pro

**Resume Critic Pro** is a Python-based AI resume analyzer built with Streamlit. It enables users to upload their resumes (PDF or DOCX) and receive instant, detailed feedback on grammar, structure, keyword usage, and career alignment. This smart tool empowers job seekers to optimize their resumes and plan personalized career growth.

---

## 🚀 Features

- 📂 **Multi-format Support**: Accepts `.pdf` and `.docx` resume files.
- 🧠 **Grammar & Writing Analysis**: Highlights grammar issues using NLP (`language_tool_python`).
- 🧱 **Structure Checker**: Detects missing key resume sections like Summary, Experience, Projects, etc.
- 🗝️ **Keyword Analysis**: Extracts the most frequent terms to assess focus and relevance.
- 🎯 **Career Path Suggestions** *(Goal-based)*: Users choose a career (e.g., Data Science, Web Dev), and the app recommends missing skills and paths using heuristics and A* search logic.
- 💡 **Smart Suggestions**: Offers actionable tips to improve tone, formatting, and professionalism.
- 📊 **Interactive Visuals**: Shows score breakdowns via pie charts.
- 📥 **Downloadable Feedback Report**: Provides a detailed `.txt` file with all feedback.

---

## 🖥️ Tech Stack

| Tool | Purpose |
|------|---------|
| `Python` | Core programming language |
| `Streamlit` | Web UI framework |
| `PyMuPDF (fitz)` | Extract text from PDF |
| `python-docx` | Extract text from DOCX |
| `language_tool_python` | Grammar and spelling check |
| `re`, `collections` | Text parsing and keyword analysis |
| `Plotly` | Visualization (pie charts) |
| `Pandas` | Data handling for visualization |

---

**##👩‍💻 Authors**
Asna Hammad – Developer & UI Designer

Fizzah Farooq – Co-Developer & NLP Analyst

---

## 🧭 How It Works

1. **Upload your resume** (PDF or DOCX).
2. The app:
   - Extracts text using PyMuPDF or python-docx
   - Checks grammar using LanguageTool
   - Scans for standard resume sections
   - Analyzes keyword frequency
3. **User selects a target career path** (Data Science, Web Dev, etc.).
4. Based on extracted skills and chosen path, the app:
   - Recommends missing skills
   - Uses heuristic planning (A* logic planned) to suggest a roadmap
5. **Detailed feedback** and **score breakdown** are displayed.
6. Users can **download** a feedback report for future use.

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/asna-154/Resume-Critic-Pro.git
cd resume-critic-pro

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run resume_critic.py
