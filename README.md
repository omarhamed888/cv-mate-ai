# CareerSync 💼🚀  
**AI-Powered CV Enhancement Platform**

CareerSync is a Flask-based web application that leverages cutting-edge AI (Google Gemini) to review, rewrite, and analyze resumes for better compatibility with Applicant Tracking Systems (ATS). It also offers a comprehensive suite of career growth tools including job matching, interview preparation, upskilling guidance, and email writing.

---

## 🔥 Features

### 📄 CV Analysis
- **AI CV Review**: Get a score, strengths, weaknesses, and personalized suggestions.
- **CV Rewriter**: Automatically improve wording, layout, and structure for ATS.
- **ATS Scanner**: Evaluate keyword match, formatting issues, and optimization.
- **CV vs Job Match**: Compare your CV against a job description and receive a match score with gap analysis.

### 💼 Interview Preparation
- **Mock Interview Generator**: Practice with realistic, AI-generated questions.
- **Job-Specific Questions**: Receive technical, general, and behavioral questions.
- **Answer Templates**: Generate professional model answers to common interview questions.

### 📈 Career Growth Tools
- **Mini Courses**: Personalized short courses based on your CV.
- **Career Path Recommendations**: Top 3 career transitions, skill gaps, and action steps.
- **Project Suggestions**: Tailored project ideas to strengthen your portfolio.

### 🧰 Bonus Utilities
- **CV Format Generator**: Apply professional or creative layouts to your resume.
- **AI Email Writer**: Craft job applications, thank-you notes, and follow-ups.
- **Job Finder (Mock)**: Explore role matches (API integration pending).

---

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/careersync.git
cd careersync
````

### 2. Install dependencies

```bash
pip install flask weasyprint python-docx PyPDF2 google-generativeai werkzeug
```

### 3. Set your Gemini API key

```bash
export GEMINI_API_KEY='your-api-key-here'  # For Linux/macOS
# Or use a .env file or insert directly in `app.py` for testing
```

### 4. Create folder structure

Ensure this directory layout:

```
cv_project/
├── app.py
├── uploads/
├── templates/
│   ├── index.html
│   ├── cv_review.html
│   ├── cv_rewriter.html
│   ├── ats_scanner.html
│   ├── job_match.html
│   ├── mock_interview.html
│   ├── job_questions.html
│   ├── answer_templates.html
│   ├── mini_courses.html
│   ├── career_paths.html
│   ├── project_suggestions.html
│   ├── job_finder.html
│   ├── cv_format.html
│   └── email_writer.html
```

### 5. Run the app

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) to start.

---

## 🧪 Testing

* Upload a `.pdf`, `.docx`, or `.txt` CV via the homepage.
* Use the top menu to explore each tool.
* Access `/debug` to inspect session variables (like `cv_text`, `improved_cv`).

---

## 💡 Upcoming Features

* 🔍 Real-time job board integration (LinkedIn/Indeed API)
* 🧠 ChatGPT fallback or dual analysis toggle
* 🌐 Multilingual CV support
* 🧾 Cover letter generator
* 🎯 Goal tracker + weekly progress dashboard

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License. See `LICENSE` file for details.

---

## ✨ Credits

* Built with Flask + Tailwind CSS
* Powered by [Google Gemini API](https://ai.google.dev)
* Developed by \[Your Name / Team Name]


