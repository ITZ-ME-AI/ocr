from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import pytesseract
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure allowed extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video(video_path, keyword):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False, "Error opening video file"

    # Process every 100th frame to improve performance
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 100 != 0:
            continue

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get better text detection
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Perform OCR
        text = pytesseract.image_to_string(thresh)
        
        # Check if keyword is in the text
        if keyword.lower() in text.lower():
            cap.release()
            return True, None

    cap.release()
    return False, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-text', methods=['POST'])
def check_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload MP4, AVI, or MOV files.'}), 400

    # Get keyword from form data
    keyword = request.form.get('keyword', '').strip()
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        contains_text, error = process_video(filepath, keyword)
        
        # Clean up the uploaded file
        os.remove(filepath)

        if error:
            return jsonify({'error': error}), 400

        return jsonify({'contains': contains_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
