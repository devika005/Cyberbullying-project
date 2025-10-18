import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import sqlite3
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import os
import requests

# Model training and retraining
class CyberbullyingModel:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', LogisticRegression())
        ])
        self.is_trained = False

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        self.is_trained = True

    def predict(self, content: str) -> bool:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        prediction = self.model.predict([content])
        return bool(prediction)

# Sample dataset for training
X_train = ["I hate you", "You are stupid", "You are amazing", "Have a great day"]
y_train = [1, 1, 0, 0]

# Initialize and train the model
model = CyberbullyingModel()
model.train(X_train, y_train)

# Database setup
db_path = 'cyberbullying.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create a table to store cyberbullying reports
c.execute('''CREATE TABLE IF NOT EXISTS reports
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              content TEXT,
              user_ip TEXT,
              account_name TEXT,
              timestamp DATETIME)''')

def report_cyberbullying(content: str, user_ip: str, account_name: str):
    timestamp = datetime.now()
    c.execute("INSERT INTO reports (content, user_ip, account_name, timestamp) VALUES (?, ?, ?, ?)",
              (content, user_ip, account_name, timestamp))
    conn.commit()
    block_user(account_name)

def block_user(account_name: str):
    block_duration = timedelta(hours=1)
    unblock_time = datetime.now() + block_duration
    print(f"User {account_name} is blocked until {unblock_time}")
    redirect_to_video()

def redirect_to_video():
    video_url = "http://example.com/educational_video"
    print(f"Redirecting user to {video_url}")

def get_user_ip():
    try:
        ip = requests.get('https://api.ipify.org').text
        return ip
    except Exception as e:
        print(f"Could not get IP address: {e}")
        return "Unknown IP"

def handle_message(content: str, account_name: str):
    user_ip = get_user_ip()
    if model.predict(content):
        report_cyberbullying(content, user_ip, account_name)
        print("Message blocked and reported.")
    else:
        print("Message allowed.")
        send_message_to_public_area(content, account_name)

def send_message_to_public_area(content: str, account_name: str):
    print(f"Message from {account_name}: {content}")

# Example usage
handle_message("I hate you", "User123")
handle_message("Have a great day", "User456")

# YouTube Integration
def fetch_youtube_comments(video_id):
    api_key = 'YOUR_API_KEY'
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()

    comments = []
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
        author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        comments.append((comment, author))

    return comments

def handle_youtube_comments(video_id):
    comments = fetch_youtube_comments(video_id)
    for comment, author in comments:
        handle_message(comment, author)

# Example usage with YouTube video ID
youtube_video_id = 'VIDEO_ID'
handle_youtube_comments(youtube_video_id)

# Instagram Integration
def fetch_instagram_comments(post_id, access_token):
    url = f"https://graph.instagram.com/{post_id}/comments?access_token={access_token}"
    response = requests.get(url)
    data = response.json()
    
    comments = []
    for comment in data.get('data', []):
        text = comment.get('text', '')
        username = comment.get('username', 'Unknown User')
        comments.append((text, username))
    
    return comments

def handle_instagram_comments(post_id, access_token):
    comments = fetch_instagram_comments(post_id, access_token)
    for comment, author in comments:
        handle_message(comment, author)

# Example usage with Instagram post ID and access token
instagram_post_id = 'INSTAGRAM_POST_ID'
instagram_access_token = 'YOUR_INSTAGRAM_ACCESS_TOKEN'
handle_instagram_comments(instagram_post_id, instagram_access_token)

conn.close()
