from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import whisper
import moviepy.editor as mp
from datetime import timedelta
import tempfile
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Whisper model (base model for faster processing, can be upgraded to large-v2 for better accuracy)
model = whisper.load_model("base")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, audio_path):
    """Extract audio from video file"""
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, verbose=False, logger=None)
    video.close()

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt(transcription_result, output_path):
    """Generate SRT subtitle file from Whisper transcription"""
    segments = transcription_result.get("segments", [])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
    
    return output_path

def generate_vtt(transcription_result, output_path):
    """Generate VTT subtitle file from Whisper transcription"""
    segments = transcription_result.get("segments", [])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        
        for segment in segments:
            start_time = format_timestamp(segment['start']).replace(',', '.')
            end_time = format_timestamp(segment['end']).replace(',', '.')
            text = segment['text'].strip()
            
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
    
    return output_path

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    language = request.form.get('language', 'en')  # Default to English
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: MP4, AVI, MOV, MKV, WEBM"}), 400
    
    try:
        # Save uploaded file
        filename = file.filename
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(video_path)
        
        # Extract audio
        audio_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}.wav")
        extract_audio(video_path, audio_path)
        
        # Transcribe audio using Whisper
        # Supported languages: en, es, fr, de, it, pt, ja, zh, ko, etc.
        transcription_result = model.transcribe(
            audio_path,
            language=language if language != 'auto' else None,
            task="transcribe"
        )
        
        # Generate subtitle files
        base_name = os.path.splitext(filename)[0]
        srt_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.srt")
        vtt_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.vtt")
        
        generate_srt(transcription_result, srt_path)
        generate_vtt(transcription_result, vtt_path)
        
        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return jsonify({
            "success": True,
            "message": "Video processed successfully",
            "video_id": base_name,
            "transcription": transcription_result.get("text", ""),
            "segments": transcription_result.get("segments", []),
            "language": transcription_result.get("language", language)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<video_id>/<format>', methods=['GET'])
def download_subtitle(video_id, format):
    """Download subtitle file in SRT or VTT format"""
    if format not in ['srt', 'vtt']:
        return jsonify({"error": "Invalid format. Use 'srt' or 'vtt'"}), 400
    
    file_path = os.path.join(OUTPUT_FOLDER, f"{video_id}.{format}")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Subtitle file not found"}), 404
    
    return send_file(file_path, as_attachment=True, download_name=f"{video_id}.{format}")

@app.route('/api/video/<video_id>', methods=['GET'])
def get_video(video_id):
    """Get the original video file"""
    # Try to find the video file
    for ext in ALLOWED_EXTENSIONS:
        video_path = os.path.join(UPLOAD_FOLDER, f"{video_id}.{ext}")
        if os.path.exists(video_path):
            return send_file(video_path)
    
    return jsonify({"error": "Video file not found"}), 404

if __name__ == '__main__':
    print("Starting Cerevyn Video-to-Subtitle API...")
    print("Loading Whisper model (this may take a moment)...")
    app.run(debug=True, port=5000, host='0.0.0.0')