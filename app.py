import os
from flask import Flask, request, render_template, jsonify
import cv2
import numpy as np
import pytesseract
from werkzeug.utils import secure_filename
from multiprocessing import Pool, cpu_count
import math

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_frame(frame_data):
    frame, frame_number = frame_data
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Perform text detection
    text = pytesseract.image_to_string(threshold)
    
    return 'abcd' in text.lower()

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate number of frames to process (1 frame per second)
    frames_to_process = min(total_frames, int(fps * 60))  # Process at most 1 minute worth of frames
    frame_interval = max(1, total_frames // frames_to_process)
    
    frames = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            frames.append((frame, frame_count))
            
        frame_count += 1
        if len(frames) >= frames_to_process:
            break
    
    cap.release()
    
    # Use multiprocessing to process frames in parallel
    num_cores = min(cpu_count(), 3)  # Use at most 3 cores
    with Pool(num_cores) as pool:
        results = pool.map(process_frame, frames)
    
    return any(results)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            result = process_video(filepath)
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify({'found': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True) 