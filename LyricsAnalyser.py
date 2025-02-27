import time
import torch
from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
import yake


# Load Hugging Face NLP models
print("Loading models... (this may take a while on first run)")
emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=3)
keywords_model = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")




# Load BART model for keyword extraction
keyword_model_name = "facebook/bart-large-cnn"  # More general text summarization model
keyword_tokenizer = AutoTokenizer.from_pretrained(keyword_model_name)
keyword_model = AutoModelForSeq2SeqLM.from_pretrained(keyword_model_name)

# Configure YAKE keyword extractor
keyword_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=5)

def extract_keywords(text):
    """Extracts key phrases using YAKE."""
    keywords = keyword_extractor.extract_keywords(text)
    
    return [kw[0] for kw in keywords]  # Return only the keyword strings



def extract_lyrics_themes(lyrics):
    """
    Extracts keywords and emotions from lyrics.
    Returns: (top_emotions, keywords)
    """
    if not lyrics.strip():
        return ["neutral"], ["unknown"]  # Handle empty lyrics case

    # Get emotions
    emotions = emotion_model(lyrics)
    top_emotions = [e['label'] for e in emotions[0]]  # Extract top 3 emotions

    # Extract keywords using YAKE (NEW)
    keywords = extract_keywords(lyrics)


    return top_emotions, keywords


def real_time_lyrics_analysis():
    """Fetches Spotify lyrics and runs real-time NLP analysis."""
    
    print("🎵 Waiting for Spotify song...")

    # Get current song and artist
    song, artist, _ = get_current_song()
    
    if song == "No song playing":
        print("🚫 No song detected. Play something on Spotify!")
        return

    print(f"🎶 Now Playing: {song} by {artist}")

    # Fetch synced lyrics with error handling
    lyrics_result = get_lyrics(song, artist)

    # Debugging output
    print(f"🧐 DEBUG: get_lyrics() returned -> {lyrics_result}")
    

    if isinstance(lyrics_result, tuple) and len(lyrics_result) >= 2:
        lyrics_data, timestamps = lyrics_result[:2]  # Unpack first two elements
    else:
        print("❌ Error: get_lyrics() did not return expected values.")
        return

    print("✅ Lyrics Found! Starting real-time analysis...")

    # Start syncing lyrics with real-time playback
    while True:
        song, artist, current_progress = get_current_song()
        if song == "No song playing":
            print("🚫 Song stopped. Exiting...")
            break

        # Find the closest timestamp
        closest_time = min(timestamps, key=lambda t: abs(convert_to_seconds(t) - current_progress))
        current_lyric = lyrics_data.get(closest_time, "🎵...")

        # Run NLP analysis
        emotions, keywords = extract_lyrics_themes(current_lyric)

        # Print results
        print("\n🎤", current_lyric)
        print(f"🎭 Emotions: {emotions}")
        print(f"🔑 Keywords: {keywords}")

        time.sleep(2)  # Wait 2 sec before checking again

# Run real-time lyrics analysis
real_time_lyrics_analysis()
