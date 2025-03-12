import time
import torch
from transformers import pipeline
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
import yake
from sentence_transformers import SentenceTransformer, util
import json
import os
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import Label

# Load Hugging Face NLP models
print("Loading models... (this may take a while on first run)")
emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=3)

# Configure YAKE keyword extractor
keyword_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=5)

# Load Sentence Transformer model for semantic similarity
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load emoji data from local directory
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

def generate_emoji_image(emojis, filename='emoji_output.png'):
    """Generates an image from a list of emojis."""
    img = Image.new('RGB', (200, 200), color = (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 80), ''.join(emojis), font=font, fill=(0, 0, 0))
    img.save(filename)

def show_emoji_gui(emojis):
    """Display emojis in a simple GUI window."""
    root = tk.Tk()
    root.title("Emoji Display")
    label = Label(root, text=' '.join(emojis), font=("Arial", 60))
    label.pack(pady=20)
    root.mainloop()

def extract_lyrics_themes(lyrics):
    """Extracts keywords, emotions, and corresponding emojis from lyrics."""
    if not lyrics.strip():
        return ["neutral"], ["unknown"], ["❓"]

    emotions = emotion_model(lyrics)
    top_emotions = [e['label'] for e in emotions[0]]
    keywords = extract_keywords(lyrics)
    emojis = map_keywords_to_emojis(keywords)

    return top_emotions, keywords, emojis

def real_time_lyrics_analysis():
    """Fetches Spotify lyrics and runs real-time NLP analysis."""

    print("\U0001F3B5 Waiting for Spotify song...")
    song, artist, _ = get_current_song()

    if song == "No song playing":
        print("\u274C No song detected. Play something on Spotify!")
        return

    print(f"\U0001F3B6 Now Playing: {song} by {artist}")

    lyrics_result = get_lyrics(song, artist)
    print(f"\U0001F9D0 DEBUG: get_lyrics() returned -> {lyrics_result}")

    if isinstance(lyrics_result, tuple) and len(lyrics_result) >= 2:
        lyrics_data, timestamps = lyrics_result[:2]
    else:
        print("\u274C Error: get_lyrics() did not return expected values.")
        return

    print("\u2705 Lyrics Found! Starting real-time analysis...")

    while True:
        song, artist, current_progress = get_current_song()
        if song == "No song playing":
            print("\u274C Song stopped. Exiting...")
            break

        closest_time = min(timestamps, key=lambda t: abs(convert_to_seconds(t) - current_progress))
        current_lyric = lyrics_data.get(closest_time, "\U0001F3B5...")

        emotions, keywords, emojis = extract_lyrics_themes(current_lyric)

        print("\n\U0001F3A4", current_lyric)
        print(f"\U0001F3AD Emotions: {emotions}")
        print(f"\U0001F511 Keywords: {keywords}")
        print(f"\U0001F49C Emojis: {emojis}")

        generate_emoji_image(emojis)
        show_emoji_gui(emojis)

        time.sleep(2)  # Wait 2 sec before checking again

# Run real-time lyrics analysis
real_time_lyrics_analysis()