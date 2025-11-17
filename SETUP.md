# Cerevyn Video-to-Subtitle Setup Guide

## Prerequisites

### Python Environment
- Python 3.8 or higher
- FFmpeg (required for video processing)

### Node.js Environment
- Node.js 14 or higher
- npm (comes with Node.js)

## Installation Steps

### 1. Install FFmpeg

**Windows:**
- Download from https://ffmpeg.org/download.html
- Extract and add to PATH, or install via chocolatey: `choco install ffmpeg`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### 2. Setup Python Backend

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Setup Node.js Frontend

```bash
# Install Node.js dependencies
npm install
```

## Running the Application

### Terminal 1 - Start Python Backend
```bash
# Make sure virtual environment is activated
python app.py
```
Backend will run on http://localhost:5000

### Terminal 2 - Start Node.js Frontend
```bash
npm start
```
Frontend will run on http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Upload a video file (MP4, AVI, MOV, MKV, WEBM)
3. Select language (or use auto-detect)
4. Click "Process Video"
5. Wait for processing to complete
6. View subtitles and download SRT or VTT files

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Japanese (ja)
- Chinese (zh)
- Korean (ko)
- Auto-detect

## Notes

- First run will download Whisper model (~150MB for base model)
- Processing time depends on video length and system performance
- Ensure both servers are running before using the application

