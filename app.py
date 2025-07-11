from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import google.generativeai as genai
import os
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import json
import re

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=GEMINI_API_KEY)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text_from_txt(file_path):
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
    return text

def extract_text_from_file(file_path):
    extension = file_path.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        return extract_text_from_txt(file_path)
    return ""

def clean_api_response(response_text):
    cleaned_text = re.sub(r'^```json\n|\n```$', '', response_text, flags=re.MULTILINE)
    return cleaned_text.strip()

def get_generative_model():
    try:
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"Error with gemini-2.0-flash: {e}")
        try:
            return genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            print(f"Error with gemini-1.5-pro: {e}")
            return genai.GenerativeModel('gemini-1.5-flash')

model = get_generative_model()

def analyze_cv_with_gemini(cv_text, analysis_type="review", job_description=""):
    try:
        if analysis_type == "review":
            prompt = f"""
            Analyze this CV and provide a comprehensive review:
            CV Content: {cv_text}
            Provide:
            1. Overall Score (out of 100)
            2. Strengths (list 5-7 key strengths)
            3. Weaknesses (list 5-7 areas for improvement)
            4. Specific recommendations for improvement
            5. Industry-specific feedback
            Format as JSON:
            {{
                "score": number,
                "strengths": [list of strings],
                "weaknesses": [list of strings],
                "recommendations": [list of strings],
                "industry_feedback": "string"
            }}
            """
        elif analysis_type == "ats":
            prompt = f"""
            Analyze this CV for ATS compatibility:
            CV Content: {cv_text}
            Provide:
            1. ATS Score (out of 100)
            2. Keyword optimization score
            3. Format compatibility issues
            4. Missing keywords/skills
            5. Specific ATS improvements needed
            Format as JSON:
            {{
                "ats_score": number,
                "keyword_score": number,
                "format_issues": [list of strings],
                "missing_keywords": [list of strings],
                "improvements": [list of strings]
            }}
            """
        elif analysis_type == "job_match":
            prompt = f"""
            Compare this CV against the job description:
            CV Content: {cv_text}
            Job Description: {job_description}
            Provide:
            1. Match Score (out of 100)
            2. Matched skills and qualifications
            3. Missing requirements
            4. Recommendations to improve match
            5. Gap analysis
            Format as JSON:
            {{
                "match_score": number,
                "matched_skills": [list of strings],
                "missing_requirements": [list of strings],
                "recommendations": [list of strings],
                "gap_analysis": "string"
            }}
            """
        elif analysis_type == "rewrite":
            prompt = f"""
            Rewrite this CV for better grammar, wording, and format:
            Original CV: {cv_text}
            Provide:
            1. Improved CV text
            2. Summary of changes made
            3. Formatting suggestions
            Format as JSON:
            {{
                "improved_cv": "string",
                "changes_made": [list of strings],
                "formatting_suggestions": [list of strings]
            }}
            """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in analyze_cv_with_gemini: {e}")
        return {"error": str(e)}

def generate_email_with_gemini(email_type, context):
    try:
        if email_type == "application":
            prompt = f"""
            Generate a professional job application email:
            Context: {context}
            Include:
            1. Appropriate subject line
            2. Professional greeting
            3. Brief introduction
            4. Relevant experience highlights
            5. Professional closing
            Format as JSON:
            {{
                "subject": "string",
                "email_body": "string",
                "tips": [list of strings]
            }}
            """
        elif email_type == "follow_up":
            prompt = f"""
            Generate a professional follow-up email:
            Context: {context}
            Include:
            1. Appropriate subject line
            2. Professional greeting
            3. Polite reminder of previous application
            4. Reaffirm interest
            5. Professional closing
            Format as JSON:
            {{
                "subject": "string",
                "email_body": "string",
                "tips": [list of strings]
            }}
            """
        elif email_type == "thank_you":
            prompt = f"""
            Generate a professional thank you email after interview:
            Context: {context}
            Include:
            1. Appropriate subject line
            2. Professional greeting
            3. Thank you for the interview
            4. Reiterate interest and key points
            5. Professional closing
            Format as JSON:
            {{
                "subject": "string",
                "email_body": "string",
                "tips": [list of strings]
            }}
            """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in generate_email_with_gemini: {e}")
        return {"error": str(e)}

def generate_interview_questions(cv_text, job_description=""):
    try:
        prompt = f"""
        Generate job-specific interview questions based on this CV and optional job description:
        CV Content: {cv_text}
        Job Description: {job_description}
        Provide:
        1. General questions (3-5)
        2. Technical questions (3-5)
        3. Behavioral questions (3-5)
        Format as JSON:
        {{
            "general_questions": [list of strings],
            "technical_questions": [list of strings],
            "behavioral_questions": [list of strings]
        }}
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in generate_interview_questions: {e}")
        return {"error": str(e)}

def generate_answer_templates(cv_text, question):
    try:
        prompt = f"""
        Generate answer templates for the following interview question based on this CV:
        CV Content: {cv_text}
        Question: {question}
        Provide 2-3 example answers in professional tone.
        Format as JSON:
        {{
            "question": "string",
            "answers": [list of strings]
        }}
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in generate_answer_templates: {e}")
        return {"error": str(e)}

def recommend_career_paths(cv_text):
    try:
        prompt = f"""
        Analyze this CV and recommend career paths:
        CV Content: {cv_text}
        Provide:
        1. Top 3 career paths
        2. Required skills for each path
        3. Steps to transition
        Format as JSON:
        {{
            "career_paths": [
                {{
                    "path": "string",
                    "required_skills": [list of strings],
                    "transition_steps": [list of strings]
                }}
            ]
        }}
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in recommend_career_paths: {e}")
        return {"error": str(e)}

def suggest_projects(cv_text):
    try:
        prompt = f"""
        Suggest small projects to strengthen this CV:
        CV Content: {cv_text}
        Provide:
        1. Project ideas (3-5)
        2. Skills developed
        3. Estimated completion time
        Format as JSON:
        {{
            "projects": [
                {{
                    "idea": "string",
                    "skills_developed": [list of strings],
                    "estimated_time": "string"
                }}
            ]
        }}
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in suggest_projects: {e}")
        return {"error": str(e)}

def generate_cv_format(cv_text, format_style):
    try:
        prompt = f"""
        Reformat this CV in the specified style:
        CV Content: {cv_text}
        Format Style: {format_style}
        Provide:
        1. Reformatted CV text
        2. Formatting notes
        Format as JSON:
        {{
            "reformatted_cv": "string",
            "formatting_notes": [list of strings]
        }}
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in generate_cv_format: {e}")
        return {"error": str(e)}

def generate_mini_course(cv_text):
    try:
        prompt = f"""
        Generate a mini career course based on this CV:
        CV Content: {cv_text}
        Provide:
        1. Course title
        2. Modules (3-5)
        3. Learning objectives
        Format as JSON:
        {{
            "title": "string",
            "modules": [list of strings],
            "objectives": [list of strings]
        }}
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_api_response(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error in generate_mini_course: {e}")
        return {"error": str(e)}

@app.route('/')
def home():
    session['cv_uploaded'] = session.get('cv_uploaded', False)
    return render_template('index.html', cv_uploaded=session['cv_uploaded'])

# CV Analysis Services Routes
@app.route('/cv-analysis/review')
def cv_review():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('cv_review.html')

@app.route('/cv-analysis/ats')
def ats_scanner():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('ats_scanner.html')

@app.route('/cv-analysis/job-match')
def job_match():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('job_match.html')

@app.route('/cv-analysis/rewriter')
def cv_rewriter():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('cv_rewriter.html')

# Interview Preparation Tools Routes
@app.route('/interview-prep/mock-interview')
def mock_interview_page():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('mock_interview.html')

@app.route('/interview-prep/job-questions')
def job_questions():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('job_questions.html')

@app.route('/interview-prep/answer-templates')
def answer_templates():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('answer_templates.html')

# Career Upskilling Tools Routes
@app.route('/upskilling/mini-courses')
def mini_courses():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('mini_courses.html')

@app.route('/upskilling/career-paths')
def career_paths_page():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('career_paths.html')

@app.route('/upskilling/project-suggestions')
def project_suggestions_page():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('project_suggestions.html')

# Bonus Tools Routes
@app.route('/bonus-tools/job-finder')
def job_finder():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('job_finder.html')

@app.route('/bonus-tools/cv-format')
def cv_format_page():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('cv_format.html')

@app.route('/bonus-tools/email-writer')
def email_writer():
    if not session.get('cv_uploaded', False):
        flash('Please upload a CV to access this feature.', 'warning')
        return redirect(url_for('home'))
    return render_template('email_writer.html')

@app.route('/upload-cv', methods=['POST'])
def upload_cv():
    if 'cv_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['cv_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        cv_text = extract_text_from_file(file_path)
        
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
        
        if not cv_text.strip():
            return jsonify({'error': 'Could not extract text from file'}), 400
        
        session['cv_text'] = cv_text
        session['cv_uploaded'] = True
        return jsonify({'cv_text': cv_text, 'redirect': url_for('home')})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze-cv', methods=['POST'])
def analyze_cv():
    data = request.json
    cv_text = data.get('cv_text', session.get('cv_text', ''))
    analysis_type = data.get('analysis_type', 'review')
    job_description = data.get('job_description', '')
    
    if not cv_text.strip():
        return jsonify({'error': 'CV text is required'}), 400
    
    result = analyze_cv_with_gemini(cv_text, analysis_type, job_description)
    return jsonify(result)

@app.route('/generate-email', methods=['POST'])
def generate_email():
    data = request.json
    email_type = data.get('email_type', 'application')
    context = data.get('context', '')
    
    if not context.strip():
        return jsonify({'error': 'Context is required'}), 400
    
    result = generate_email_with_gemini(email_type, context)
    return jsonify(result)

@app.route('/mock-interview', methods=['POST'])
def mock_interview():
    data = request.json
    cv_text = data.get('cv_text', session.get('cv_text', ''))
    job_description = data.get('job_description', '')
    
    if not cv_text.strip():
        return jsonify({'error': 'CV text is required'}), 400
    
    result = generate_interview_questions(cv_text, job_description)
    return jsonify(result)

@app.route('/answer-template', methods=['POST'])
def answer_template():
    data = request.json
    cv_text = data.get('cv_text', session.get('cv_text', ''))
    question = data.get('question', '')
    
    if not cv_text.strip() or not question.strip():
        return jsonify({'error': 'CV text and question are required'}), 400
    
    result = generate_answer_templates(cv_text, question)
    return jsonify(result)

@app.route('/career-paths', methods=['POST'])
def career_paths():
    cv_text = session.get('cv_text', '')
    if not cv_text.strip():
        return jsonify({'error': 'CV text is required'}), 400
    
    result = recommend_career_paths(cv_text)
    return jsonify(result)

@app.route('/project-suggestions', methods=['POST'])
def project_suggestions():
    cv_text = session.get('cv_text', '')
    if not cv_text.strip():
        return jsonify({'error': 'CV text is required'}), 400
    
    result = suggest_projects(cv_text)
    return jsonify(result)

@app.route('/cv-format', methods=['POST'])
def cv_format():
    data = request.json
    cv_text = data.get('cv_text', session.get('cv_text', ''))
    format_style = data.get('format_style', 'professional')
    
    if not cv_text.strip():
        return jsonify({'error': 'CV text is required'}), 400
    
    result = generate_cv_format(cv_text, format_style)
    return jsonify(result)

@app.route('/mini-course', methods=['POST'])
def mini_course():
    cv_text = session.get('cv_text', '')
    if not cv_text.strip():
        return jsonify({'error': 'CV text is required'}), 400
    
    result = generate_mini_course(cv_text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)