from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수(API 키)를 불러옵니다.
load_dotenv()

app = Flask(__name__)
# frontend 폴더에서 오는 요청을 허용해줍니다 (CORS 문제 해결).
CORS(app)

# Gemini API 설정
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return jsonify({"error": "Gemini API key is not configured on the server. Please check your .env file."}), 500

    data = request.json
    if not data or 'image_data' not in data:
        return jsonify({"error": "No image data provided."}), 400

    image_data = data['image_data']
    mime_type = data.get('mime_type', 'image/jpeg')

    prompt = """
    You are an expert at analyzing university timetables from the 'Everytime' app.
    Analyze the provided image. Identify all the class blocks.
    For each class, determine the day of the week and its start and end times.
    The grid starts at 9 AM at the top. Each major grid line represents one hour. A class spanning one and a half grid cells is a 1.5-hour class.
    Provide the output ONLY as a clean JSON array of objects, without any markdown formatting like ```json.
    Each object must have three keys:
    1. "day": string, one of '월', '화', '수', '목', '금'.
    2. "start": number, the start time in 24-hour format (e.g., 13.5 for 1:30 PM).
    3. "end": number, the end time in 24-hour format (e.g., 15.0 for 3:00 PM).
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": image_data}}
            ]
        }]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60 # 60초 타임아웃 설정
        )
        response.raise_for_status()  # HTTP error checking
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to call Gemini API."}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

