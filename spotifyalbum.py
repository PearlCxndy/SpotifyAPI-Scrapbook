from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QColorDialog
from LyricsFetcher import get_lyrics
from spotifylyrics import get_current_song
import requests
from PIL import Image
from io import BytesIO

def get_dominant_color(image):
    """Get the dominant color from the album art."""
    image = image.resize((150, 150))  
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
        track_name, artist_name, album_art_url = get_current_song()
        if track_name and artist_name and album_art_url:
            response = requests.get(album_art_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            dominant_color = get_dominant_color(image)
            hex_color = rgb_to_hex(dominant_color)
            lyrics_dict, _ = get_lyrics(track_name, artist_name)
            lyrics_text = "\n".join([f"[{time}] {lyric}" for time, lyric in lyrics_dict.items()]) if lyrics_dict else "Lyrics not found."

            return {
                "track_name": track_name,
                "artist_name": artist_name,
                "album_art_url": album_art_url,
                "dominant_color": hex_color,
                "lyrics": lyrics_text,
                "image": image
            }
    except Exception as e:
        print(f"Error fetching track data: {e}")
    return None

def set_canvas_bg_from_album(app_instance):
    """Set the drawing label's background color using album art's dominant color."""
    track_data = fetch_current_track_data()
    if track_data and track_data.get("dominant_color"):
        color = QColor(track_data["dominant_color"])
        app_instance.bg_label.setStyleSheet(f"background-color: {color.name()};")
        print(f"Auto-set background color to {color.name()}")

def pick_canvas_bg_color(app_instance):
    """Open color picker and set the chosen color as background."""
    color = QColorDialog.getColor()
    if color.isValid():
        app_instance.bg_label.setStyleSheet(f"background-color: {color.name()};")
        print(f"Manual background color set to {color.name()}")
