# personalized_study_assistant.py

# Import necessary libraries
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import openai

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Database setup
DATABASE_URL = "sqlite:///study_assistant.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

Base.metadata.create_all(engine)

# Configure OpenAI API
openai.api_key = "your_openai_api_key"

# Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_note():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Process the uploaded file
    with open(filepath, 'r') as f:
        content = f.read()
    title = request.form.get("title", "Untitled")
    
    # Save to database
    new_note = Note(title=title, content=content)
    session.add(new_note)
    session.commit()

    return jsonify({"message": "File uploaded and saved", "id": new_note.id})

@app.route('/notes', methods=['GET'])
def list_notes():
    notes = session.query(Note).all()
    return jsonify([{"id": note.id, "title": note.title, "content": note.content} for note in notes])

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    note_id = request.json.get('note_id')
    note = session.query(Note).get(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    # Generate quiz using LLM
    prompt = f"Create 5 quiz questions based on the following text:\n{note.content}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    quiz = response.choices[0].text.strip()
    return jsonify({"quiz": quiz})

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    note_id = request.json.get('note_id')
    note = session.query(Note).get(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    # Generate summary using LLM
    prompt = f"Summarize the following text:\n{note.content}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    summary = response.choices[0].text.strip()
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
