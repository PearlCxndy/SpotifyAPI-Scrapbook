import requests
from PIL import Image
from io import BytesIO
from LyricsFetcher import get_lyrics
from spotifylyrics import get_current_song

def get_dominant_color(image):
    """Get the dominant color from the album art."""
    image = image.resize((150, 150))  # Resize for faster processing
    image = image.convert('RGB')
    pixels = list(image.getdata())
    dominant_color = max(set(pixels), key=pixels.count)
    return dominant_color

def rgb_to_hex(rgb):
    """Convert RGB to HEX."""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def fetch_current_track_data():
    """Fetch the currently playing track's data (album art, lyrics, dominant color)."""
    try:
        # Fetch the currently playing song
        track_name, artist_name, album_art_url = get_current_song()
        if track_name and artist_name and album_art_url:
            # Fetch album art
            response = requests.get(album_art_url)
            response.raise_for_status()  # Raise an error for bad responses
            image = Image.open(BytesIO(response.content))
            
            # Get dominant color
            dominant_color = get_dominant_color(image)
            hex_color = rgb_to_hex(dominant_color)
            
            # Fetch lyrics
            lyrics_dict, _ = get_lyrics(track_name, artist_name)
            lyrics_text = "\n".join([f"[{time}] {lyric}" for time, lyric in lyrics_dict.items()]) if lyrics_dict else "Lyrics not found."
            
            return {
                "track_name": track_name,
                "artist_name": artist_name,
                "album_art_url": album_art_url,
                "dominant_color": hex_color,
                "lyrics": lyrics_text,
                "image": image  # PIL Image object
            }
    except Exception as e:
        print(f"Error fetching track data: {e}")
    return None