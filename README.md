# Video Text Detector

This application allows users to upload videos and detect if they contain the text "abcd" using OCR (Optical Character Recognition).

## Features

- Video upload with drag-and-drop support
- Real-time video processing
- Text detection using OCR
- Modern, responsive UI
- Support for multiple video formats (MP4, AVI, MOV)

## Prerequisites

- Python 3.7+
- Tesseract OCR
- OpenCV

## Local Setup

1. Install Tesseract OCR:
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - `PYTHON_VERSION`: 3.7.0

## Notes

- Maximum file size: 16MB
- Supported video formats: MP4, AVI, MOV
- The application will automatically clean up uploaded files after processing 