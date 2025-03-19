import time
import torch
from transformers import pipeline
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
import yake
from sentence_transformers import SentenceTransformer, util
import json
import os


print("Loading models... (this may take a while on first run)")
emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=3)
keyword_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=5)
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')


emoji_data_path = os.path.join('local_emoji_data', 'emoji.json')
with open(emoji_data_path, 'r', encoding='utf-8') as f:
    emoji_data = json.load(f)
    emoji_descriptions = [item['name'].lower() for item in emoji_data]
    emoji_embeddings = similarity_model.encode(emoji_descriptions, convert_to_tensor=True)
    emoji_dict = {item['name'].lower(): item['unified'] for item in emoji_data}

def extract_keywords(text):
    """Extracts key phrases using YAKE."""
    keywords = keyword_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

def unicode_to_emoji(unicode_str):
    """Converts a Unicode string to an emoji character, handling compound codes."""
    return ''.join(chr(int(u, 16)) for u in unicode_str.split('-'))

def map_keywords_to_emojis(keywords):
    """Maps extracted keywords to emojis using semantic similarity."""
    matched_emojis = []
    for keyword in keywords:
        keyword_embedding = similarity_model.encode(keyword, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(keyword_embedding, emoji_embeddings)
        best_match_idx = torch.argmax(cosine_scores)
        best_match_desc = emoji_descriptions[best_match_idx]
        emoji_unicode = emoji_dict[best_match_desc]
        emoji_char = unicode_to_emoji(emoji_unicode)
        matched_emojis.append(emoji_char)
    return matched_emojis if matched_emojis else ["❓"]

def extract_lyrics_themes(lyrics):
    """Extracts keywords, emotions, and corresponding emojis from lyrics."""
    if not lyrics.strip():
        return ["neutral"], ["unknown"], ["❓"]

    emotions = emotion_model(lyrics)
    top_emotions = [e['label'] for e in emotions[0]]
    keywords = extract_keywords(lyrics)
    emojis = map_keywords_to_emojis(keywords)

    return top_emotions, keywords, emojis

