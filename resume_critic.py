import os
import streamlit as st
import tempfile
import fitz  # PyMuPDF
import docx
import language_tool_python
import re
from collections import Counter
import pandas as pd
import plotly.express as px

# --- Utility Functions ---
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def detect_file_type(file):
    if file.name.endswith('.pdf'):
        return 'pdf'
    elif file.name.endswith('.docx'):
        return 'docx'
    else:
        return 'unsupported'

# --- Feedback Generator ---
tool = language_tool_python.LanguageTool('en-US', config={'cacheSize': 0})

def get_resume_feedback(text):
    matches = tool.check(text)
    seen = set()
    grammar_issues = []
    for match in matches:
        issue = match.message.strip()
        if issue not in seen and not issue.lower().startswith("possible spelling mistake"):
            seen.add(issue)
            grammar_issues.append({
                "issue": issue,
                "example": text[match.offset:match.offset + match.errorLength],
                "color": f"hsl({len(grammar_issues)*60}, 70%, 80%)"  # Different color for each issue
            })
        if len(grammar_issues) == 5:
            break

    if not grammar_issues:
        grammar_section = "✅ No major grammar issues detected."
        grammar_score = 100
    else:
        grammar_section = grammar_issues
        grammar_score = max(60, 100 - len(grammar_issues) * 8)

    sections = ["summary", "skills", "projects", "experience", "education", "certifications"]
    missing_sections = []
    text_lower = text.lower()
    for section in sections:
        if section not in text_lower:
            missing_sections.append(section.capitalize())

    if not missing_sections:
        section_text = "✅ All major resume sections are present."
        section_score = 100
    else:
        section_text = f"⚠️ **Missing Sections:** {', '.join(missing_sections)}"
        section_score = max(60, 100 - len(missing_sections) * 5)

    words = re.findall(r'\b\w+\b', text.lower())
    common = Counter(words).most_common(10)
    keywords = [word for word, count in common if word.isalpha()]
    keyword_text = "💡 **Most Frequent Keywords:** " + ", ".join(keywords[:10])

    overall_score = int((grammar_score + section_score) / 2)

    return grammar_section, section_text, keyword_text, overall_score, grammar_score, section_score, missing_sections

# --- Smart Suggestions ---
def generate_smart_suggestions(score, missing_sections, keywords):
    suggestions = []
    
    if score >= 90:
        suggestions.append("🎯 Your resume is excellent! Consider adding quantifiable achievements.")
    elif score >= 70:
        suggestions.append("🎯 Good foundation. Focus on adding missing sections and quantifying results.")
    else:
        suggestions.append("🎯 Start by fixing grammar issues and adding missing sections.")
    
    if 'Projects' in missing_sections:
        suggestions.append("🛠️ Add a Projects section to showcase your work.")
    if 'Certifications' in missing_sections:
        suggestions.append("📜 Include relevant certifications with issuing organizations.")
    
    if len(keywords) > 0 and keywords[0] in ['i', 'my', 'me']:
        suggestions.append("📝 Reduce first-person pronouns for more professional tone.")
    
    suggestions.extend([
        "⏳ Use standard section headings (e.g., 'Work Experience')",
        "🔍 Quantify achievements with numbers where possible",
        "✨ Start bullet points with strong action verbs",
        "📏 Keep to 1 page unless you have 10+ years experience"
    ])
    
    return suggestions[:5]

# --- Streamlit UI ---
def main():
    # Custom CSS for professional UI
    st.set_page_config(
        page_title="Resume Critic Pro", 
        layout="centered",
        page_icon="📄"
    )
    
    st.markdown("""
        <style>
            .main {
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .stApp {
                background-color: #f8f9fa;
                display: flex;
                justify-content: center;
            }
            
            .stButton>button {
                background-color: #4b6cb7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 500;
                width: 100%;
            }
            
            .stButton>button:hover {
                background-color: #3a56a0;
            }
            
            .stFileUploader>div>div>div>div {
                color: #4b6cb7;
                border-color: #4b6cb7;
            }
            
            .feedback-card {
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #4b6cb7;
            }
            
            .score-card {
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                border-top: 4px solid #4b6cb7;
            }
            
            .suggestion-card {
                background: #f0f5ff;
                border-radius: 6px;
                padding: 1rem;
                margin: 0.75rem 0;
                font-size: 14px;
                border-left: 3px solid #4b6cb7;
            }
            
            h1, h2, h3 {
                color: #2c3e50;
                text-align: center;
            }
            
            .graph-card {
                background: white;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .header-icon {
                display: block;
                margin: 0 auto;
                text-align: center;
                font-size: 3rem;
                color: #4b6cb7;
                margin-bottom: 1rem;
            }
            
            .grammar-item {
                padding: 0.75rem;
                margin: 0.5rem 0;
                border-radius: 6px;
                border-left: 4px solid;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Header with document icon
    st.markdown('<div class="header-icon">📄</div>', unsafe_allow_html=True)
    st.title("Resume Critic Pro")
    st.markdown("""
        <div style="text-align: center; color: #4b6cb7; margin-bottom: 2rem;">
            AI-powered resume analysis and feedback
        </div>
    """, unsafe_allow_html=True)
    
    # File Upload
    uploaded_file = st.file_uploader("Choose a resume file (PDF or DOCX)", type=["pdf", "docx"])
    
    if uploaded_file:
        file_type = detect_file_type(uploaded_file)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        if file_type == 'pdf':
            resume_text = extract_text_from_pdf(tmp_path)
        elif file_type == 'docx':
            resume_text = extract_text_from_docx(tmp_path)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX file.")
            st.stop()
        
        if resume_text.strip():
            if st.button("Analyze Resume", type="primary"):
                with st.spinner("Analyzing your resume..."):
                    grammar_section, section_text, keyword_text, overall_score, grammar_score, section_score, missing_sections = get_resume_feedback(resume_text)
                    
                    # Display Results
                    st.markdown("---")
                    st.markdown("## Analysis Results")
                    
                    # Score Card
                    st.markdown(f"""
                        <div class="score-card">
                            <h2>Your Resume Score</h2>
                            <div style="font-size: 42px; font-weight: bold; color: {'#4CAF50' if overall_score >= 85 else '#FF9800' if overall_score >= 70 else '#F44336'}; margin: 10px 0;">
                                {overall_score}/100
                            </div>
                            <div style="font-size: 16px; color: #4b5563;">
                                {"Excellent! Ready for applications" if overall_score >= 85 
                                else "Good, but could use improvements" if overall_score >= 70 
                                else "Needs work - see suggestions below"}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Pie Chart Visualization
                    st.markdown("""
                        <div class="graph-card">
                            <h3 style="text-align: center;">Score Breakdown</h3>
                    """, unsafe_allow_html=True)
                    
                    # Create dataframe for pie chart
                    score_data = pd.DataFrame({
                        'Category': ['Grammar', 'Sections'],
                        'Score': [grammar_score, section_score],
                        'Color': ['#4b6cb7', '#6a4c93']
                    })
                    
                    # Create pie chart
                    fig = px.pie(score_data, 
                                values='Score', 
                                names='Category',
                                color='Color',
                                color_discrete_map={'Grammar':'#4b6cb7', 'Sections':'#6a4c93'})
                    
                    fig.update_traces(textinfo='percent+label', 
                                    pull=[0.1, 0], 
                                    marker=dict(line=dict(color='#ffffff', width=2)))
                    fig.update_layout(showlegend=False)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Feedback Columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Grammar Feedback
                        st.markdown("""
                            <div class="feedback-card">
                                <h3>Grammar & Writing</h3>
                        """, unsafe_allow_html=True)
                        
                        if isinstance(grammar_section, str):
                            st.markdown(grammar_section)
                        else:
                            for i, issue in enumerate(grammar_section):
                                st.markdown(f"""
                                    <div class="grammar-item" style="background-color: {issue['color']}; border-left-color: {issue['color'].replace('80%)', '50%)')}">
                                        <strong>• {issue['issue']}</strong><br>
                                        Example: "{issue['example']}"
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    with col2:
                        # Section Feedback
                        st.markdown(f"""
                            <div class="feedback-card">
                                <h3>Structure & Sections</h3>
                                {section_text}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Keywords
                    st.markdown(f"""
                        <div class="feedback-card">
                            <h3>Keyword Analysis</h3>
                            {keyword_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Smart Suggestions (automatically shown)
                    st.markdown("---")
                    st.markdown("## Improvement Suggestions")
                    
                    suggestions = generate_smart_suggestions(
                        overall_score, 
                        missing_sections, 
                        re.findall(r'\b\w+\b', resume_text.lower())
                    )
                    
                    for suggestion in suggestions:
                        st.markdown(f"""
                            <div class="suggestion-card">
                                {suggestion}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Download Report
                    st.markdown("---")
                    report_name = "resume_feedback_report.txt"
                    with open(report_name, "w", encoding="utf-8") as f:
                        f.write("Resume Feedback Report\n\n")
                        if isinstance(grammar_section, str):
                            f.write("Grammar & Writing:\n" + grammar_section + "\n\n")
                        else:
                            f.write("Grammar & Writing:\n")
                            for issue in grammar_section:
                                f.write(f"- {issue['issue']} → \"{issue['example']}\"\n")
                            f.write("\n")
                        f.write("Structure & Sections:\n" + section_text + "\n\n")
                        f.write("Keyword Analysis:\n" + keyword_text + "\n\n")
                        f.write(f"Overall Score: {overall_score}/100\n")
                    
                    with open(report_name, "rb") as f:
                        st.download_button(
                            label="Download Full Report",
                            data=f,
                            file_name=report_name,
                            mime="text/plain",
                            use_container_width=True
                        )
        else:
            st.warning("No readable text found in the uploaded file.")

if __name__ == "__main__":
    main()

