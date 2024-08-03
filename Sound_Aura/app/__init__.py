from flask import Flask
from flask_cors import CORS
from config import Config
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})
app.config.from_object(Config)

# Set up the cache directory
cache_dir = os.path.join(os.path.dirname(__file__), 'model_cache')
os.makedirs(cache_dir, exist_ok=True)

# Load the model and tokenizer separately
device = 0 if torch.cuda.is_available() else -1
model_name = "facebook/bart-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
# Define candidate labels
candidate_labels = [
    "target_valence", "minimum_valence", "maximum_valence", 
    "target_acousticness", "minimum_acousticness", "maximum_acousticness"
    "target_danceability", "minimum_danceability", "maximum_danceability",
    "target_energy", "minimum_energy", "maximum_energy",
    "target_instrumentalness", "minimum_instrumentalness", "maximum_instrumentalness",
    "target_liveness", "minimum_liveness", "maximum_liveness",
    "target_speechiness", "minimum_speechiness", "maximum_speechiness"
]

# Create the pipeline without passing cache_dir
spotify_recommendation_parameters = pipeline(
    "zero-shot-classification", 
    model=model,
    tokenizer=tokenizer,
    candidate_labels=candidate_labels,
    multi_label=True,
    device=device
)

def process_model_output(model_output, target_features):
    features = {}
    for label, score in zip(model_output['labels'], model_output['scores']):
        parts = label.split('_')
        if len(parts) == 2:
            prefix, feature = parts
            if prefix in ['target', 'minimum', 'maximum']:
                if prefix == 'target':
                    features[label] = score
                elif prefix == 'minimum':
                    features[f'min_{feature}'] = score
                elif prefix == 'maximum':
                    features[f'max_{feature}'] = score

    full_features = {}
    for feature in target_features:
        key1 = f'target_{feature}'
        key2 = f'minimum_{feature}'
        key3 = f'maximum_{feature}'
        
        #if key1 in features:
            #full_features[key1] = features[key1]
        if key2 in features:
            full_features[key2] = features[key2]
        if key3 in features:
            full_features[key3] = features[key3]
    
    return full_features

from app import routes