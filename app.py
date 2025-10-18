

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins":"*"}})

# NEW: Add error handling for file loading
try:
    with open("stopwords.txt", "r") as file:
        stopwords = file.read().splitlines()
    with open("tfidfvectorizer11.pkl", "rb") as f:
        vocab = pickle.load(f)    

    vectorizer = TfidfVectorizer(
        stop_words=stopwords, 
        lowercase=True, 
    )
    vectorizer.fit(vocab)
    model = pickle.load(open("models/SGDClassifier_model.pkl", 'rb'))
except Exception as e:
    print(f"!!! Error loading files: {str(e)}")  # NEW: Log loading errors
    raise  # Stop server if files fail to load



@app.route('/validate-comment', methods=['POST'])
def validate_comment():
    # NEW: Add basic input validation
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    user_input = request.json.get('text')
    if not user_input or not isinstance(user_input, str):
        return jsonify({"error": "Invalid or missing 'text' field"}), 400

    # NEW: Log the input text for debugging
    print(f"Processing comment: {user_input}")

    try:
        transformed_input = vectorizer.transform([user_input])
        prediction = model.predict(transformed_input)[0]
        return jsonify({"prediction": int(prediction)})
    except Exception as e:
        # NEW: Log prediction errors
        print(f"!!! Prediction error: {str(e)}")
        return jsonify({"error": "Failed to process comment"}), 500



if __name__ == '__main__':
    app.run(debug=True)