import os
import requests
from flask import Flask, request
from transformers import pipeline
from flask_cors import CORS
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import openai

app = Flask(__name__)
CORS(app)

# Set up Spotify authentication
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

spotify_client_credentials = SpotifyClientCredentials(
    client_id='e08ccb879b56439897b61560a3232335',
    client_secret='2acd67d0edf44c348c6a0f662b7f75b5'
)

sp = Spotify(auth_manager=spotify_client_credentials)

# Set OpenAI API key
openai.api_key = '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'

# Emotion detection pipeline
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    framework="pt",
    return_all_scores=True
)

# Function to generate dynamic response using OpenAI GPT
def generate_dynamic_response(mood, user_message):
    prompt = f"The user is feeling {mood}. Generate a friendly response acknowledging the mood and suggesting music can help."
    
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=[
            {"role": "user", "content": user_message},
        ]
    )

    
        return response.choices[0].message['content']
    except Exception as e:
        print(f'Error Occured here: {e} ')
        return "I'm here to help you with some music recommendations!"

# Function to get music recommendations from Spotify
def get_spotify_recommendations(mood):
    mood_to_genre = {
        "joy": "happy",
        "sadness": "sad",
        "anger": "chill",
        "fear": "acoustic",
        "surprise": "dance",
        "love": "romance"
    }
    
    genre = mood_to_genre.get(mood, "pop")
    results = sp.search(q=f'genre:{genre}', type='track', limit=5)
    
    recommendations = [
        f"{track['name']} by {track['artists'][0]['name']}"
        for track in results['tracks']['items']
    ]
    
    return recommendations

# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get('message')
    
    # Detect emotion
    emotions = emotion_pipeline(user_message)
    dominant_emotion = max(emotions[0], key=lambda e: e["score"])["label"]

    # Generate a dynamic response using OpenAI GPT
    dynamic_response = generate_dynamic_response(dominant_emotion, user_message)

    # Get music recommendations from Spotify
    spotify_recommendations = get_spotify_recommendations(dominant_emotion)

    return {
        "dynamic_response": dynamic_response,
        "spotify_recommendations": spotify_recommendations,
    }

if __name__ == "__main__":
    app.run(debug=True)
