import time
import torch
from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
import yake

print("Loading models... (this may take a while on first run)")
emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=3)
keywords_model = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")


keyword_model_name = "facebook/bart-large-cnn" 
keyword_tokenizer = AutoTokenizer.from_pretrained(keyword_model_name)
keyword_model = AutoModelForSeq2SeqLM.from_pretrained(keyword_model_name)

keyword_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=5)

def extract_keywords(text):
    """Extracts key phrases using YAKE."""
    keywords = keyword_extractor.extract_keywords(text)
    
    return [kw[0] for kw in keywords] 


def extract_lyrics_themes(lyrics):
    """
    Extracts keywords and emotions from lyrics.
    Returns: (top_emotions, keywords)
    """
    if not lyrics.strip():
        return ["neutral"], ["unknown"]

    emotions = emotion_model(lyrics)
    top_emotions = [e['label'] for e in emotions[0]] 

    keywords = extract_keywords(lyrics)


    return top_emotions, keywords


def real_time_lyrics_analysis():
    print("🎵 Waiting for Spotify song...")
    song, artist, _ = get_current_song()
    
    if song == "No song playing":
        print("🚫 No song detected. Play something on Spotify!")
        return

    print(f"🎶 Now Playing: {song} by {artist}")
    lyrics_result = get_lyrics(song, artist)

    print(f"🧐 DEBUG: get_lyrics() returned -> {lyrics_result}")
    

    if isinstance(lyrics_result, tuple) and len(lyrics_result) >= 2:
        lyrics_data, timestamps = lyrics_result[:2] 
    else:
        print("❌ Error: get_lyrics() did not return expected values.")
        return

    print("Lyrics Found! Starting real-time analysis...")

    while True:
        song, artist, current_progress = get_current_song()
        if song == "No song playing":
            print("Song stopped. Exiting...")
            break

        closest_time = min(timestamps, key=lambda t: abs(convert_to_seconds(t) - current_progress))
        current_lyric = lyrics_data.get(closest_time, "🎵...")
        emotions, keywords = extract_lyrics_themes(current_lyric)

        print("\n🎤", current_lyric)
        print(f"🎭 Emotions: {emotions}")
        print(f"🔑 Keywords: {keywords}")

        time.sleep(2)  

real_time_lyrics_analysis()
