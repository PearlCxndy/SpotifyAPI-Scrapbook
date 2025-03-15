
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

def convert_to_seconds(timestamp):
    """
    Converts an LRC timestamp (MM:SS.SS) to seconds.
    """
    try:
        time_obj = datetime.strptime(timestamp, "%M:%S.%f")
        return (time_obj.minute * 60) + time_obj.second + (time_obj.microsecond / 1000000)
    except ValueError:
        return 0  # Default return if parsing fails

if __name__ == "__main__":
    # Example Test
    song = "Blinding Lights"
    artist = "The Weeknd"
    
    lrc_lyrics = get_lyrics(song, artist)

    if lrc_lyrics == "No synced lyrics found.":
        print("Lyrics not found.")
    else:
        parsed_lyrics, timestamps = parse_synced_lyrics(lrc_lyrics)
        print(f"\nParsed lyrics for {song} by {artist}:\n")
        for time, lyric in parsed_lyrics.items():
            print(f"[{time}] {lyric}")
