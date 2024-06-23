from flask import Flask, request, render_template, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

app = Flask(__name__)
genai.configure(api_key='AIzaSyDkjP8rxYwgRcukcKZzlSiRZRKuNu3yhPU')
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_video_id(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([t['text'] for t in transcript])
        return text
    except Exception as e:
        return f"Error fetching transcript: {e}"

def summarize_text(text):
    try:
        prompt = f"{text}, provide a bullet-point summary of the main points and key takeaways."
        response = model.generate_content(prompt)
        summary_points = response.text.split('\n')
        formatted_summary = "\n".join([f"- {point.strip()}" for point in summary_points if point.strip()])
        return formatted_summary
    except Exception as e:
        return f"Error summarizing text: {e}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    video_url = request.form['video_url']
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'})
    transcript = fetch_transcript(video_id)
    if "Error" in transcript:
        return jsonify({'error': transcript})
    summary = summarize_text(transcript)
    if "Error" in summary:
        return jsonify({'error': summary})
    return jsonify({'transcript': transcript, 'summary': summary})

if __name__ == '__main__':
    app.run(debug=False)
