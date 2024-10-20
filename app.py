import os
import json
import requests
from flask import Flask, request
from transformers import pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load your Last.fm API key from environment variable or replace with your key
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")  # Set this in your environment


# Emotion detection pipeline
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    framework="pt",  # 'pt' for PyTorch, 'tf' for TensorFlow
    return_all_scores=True
)
# Function to get music recommendations from Last.fm API
def get_lastfm_recommendations(mood):
    # Map moods to tags that Last.fm understands
    mood_to_tag = {
        "joy": "happy",
        "sadness": "sad",
        "anger": "angry",
        "fear": "calm",
        "surprise": "exciting",
        "love": "romantic"
    }
    
    tag = mood_to_tag.get(mood, "pop")  # Default to pop if mood is unknown
    url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={tag}&api_key={LASTFM_API_KEY}&format=json"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        recommendations = [
            f"{track['name']} by {track['artist']['name']}"
            for track in data['tracks']['track'][:5]  # Get top 5 tracks
        ]
        return recommendations
    else:
        return ["Could not fetch recommendations from Last.fm."]

# Function to get music recommendations from Open Music API


# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get('message')
    
    # Detect emotion
    emotions = emotion_pipeline(user_message)
    dominant_emotion = max(emotions[0], key=lambda e: e["score"])["label"]

    # Get music recommendations from both APIs
    lastfm_recommendations = get_lastfm_recommendations(dominant_emotion)
    

    return {
        "lastfm_recommendations": lastfm_recommendations,
        
    }

if __name__ == "__main__":
    app.run(debug=True)
