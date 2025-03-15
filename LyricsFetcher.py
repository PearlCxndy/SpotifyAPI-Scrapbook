import re
from datetime import datetime
import syncedlyrics

def get_lyrics(song, artist):
    print(f"🔍 Searching lyrics for: {song} by {artist}")  # Debugging line

    # Fetch lyrics from SyncedLyrics or Genius
    lyrics_list = syncedlyrics.search(f"{song} {artist}")

    if not lyrics_list:
        print("❌ No lyrics found.")  # Debugging line
        return None  # Return None if no lyrics are found

    print("✅ Lyrics found!")  # Debugging line

    lyrics_dict = {}
    timestamps_list = []

    for line in lyrics_list.split("\n"):  # Ensure it's being split correctly
        match = re.match(r"\[(\d{2}:\d{2}.\d{2})\](.*)", line)
        if match:
            timestamp, text = match.groups()
            lyrics_dict[timestamp] = text.strip()
            timestamps_list.append(timestamp)

    return lyrics_dict, timestamps_list

def parse_synced_lyrics(lrc_text):
    """
    Parses the LRC file format and returns a dictionary mapping timestamps to lyrics.
    """
    lyrics_dict = {}  # Stores timestamps and their corresponding lyrics
    time_list = []  # Stores timestamps for easy lookup

    for line in lrc_text.split("\n"):
        line = line.strip()
        pattern = r"\[(\d{2}:\d{2}\.\d{2})\](.+)"  # Matches timestamps and lyrics
        match = re.match(pattern, line)

        if match:
            time_str = match.group(1)  # Extract timestamp (MM:SS.SS)
            lyric_text = match.group(2).strip()  # Extract lyrics

            lyrics_dict[time_str] = lyric_text
            time_list.append(time_str)

    return lyrics_dict, time_list

def convert_to_seconds(time_str):
    """Convert a timestamp string (e.g., '1:23') to seconds."""
    if not time_str or not isinstance(time_str, str):
        return None  # Handle invalid input

    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except (ValueError, AttributeError):
        return None  # Handle parsing errors