from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import sys
import time
import threading
from PyQt6.QtCore import Qt  # Import Qt for alignment options
from spotifylyrics import get_current_song  # Spotify function
from LyricsFetcher import get_lyrics, parse_synced_lyrics, convert_to_seconds  # SyncedLyrics functions

class LyricsApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize values
        self.song = "Fetching song..."
        self.artist = "Loading artist..."
        self.current_progress = 0
        self.parsed_lyrics = {}
        self.timestamps = []
        self.full_lyrics_mode = False  # Toggle between synced and full lyrics mode

        self.initUI()
        self.refresh_lyrics()  # Fetch song & lyrics on startup

        # Start a thread to update lyrics dynamically
        self.lyrics_updater = threading.Thread(target=self.update_lyrics_loop, daemon=True)
        self.lyrics_updater.start()

    def initUI(self):
        """Initialize the UI layout"""
        self.setWindowTitle("Spotify Lyrics Fetcher")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: white;")  # Set background color to white

        layout = QVBoxLayout()

        # Song title display (Centered)
        self.song_label = QLabel(f"Now Playing: {self.song} by {self.artist}")
        self.song_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center; color: black;")
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center text
        layout.addWidget(self.song_label)

        # Lyrics display (Large Font)
        self.lyrics_label = QLabel("Waiting for lyrics...")
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center; color: black;")  
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center lyrics
        layout.addWidget(self.lyrics_label)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Lyrics")
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        self.refresh_button.setStyleSheet("font-size: 14px; color: black;")  # Increase button size
        layout.addWidget(self.refresh_button)

        # Toggle full lyrics button
        self.toggle_button = QPushButton("Show Full Lyrics")
        self.toggle_button.clicked.connect(self.toggle_full_lyrics)
        self.toggle_button.setStyleSheet("font-size: 14px; color: black;")  # Increase button size
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)

    def fetch_song_info(self):
        """Fetch the currently playing song from Spotify"""
        try:
            song, artist, progress = get_current_song()
            if song and artist:
                self.current_progress = progress
                return song, artist
        except Exception as e:
            print(f"Error fetching song info: {e}")

        return "No song playing", "Unknown Artist"  # Default fallback

    def fetch_lyrics(self):
        """Fetch lyrics from SyncedLyrics"""
        if self.song == "No song playing":
            return {}, []

        try:
            lrc_lyrics = get_lyrics(self.song, self.artist)
            if lrc_lyrics == "No synced lyrics found.":
                return {}, []

            parsed_lyrics, timestamps = parse_synced_lyrics(lrc_lyrics)
            return parsed_lyrics, timestamps
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return {}, []

    def refresh_lyrics(self):
        """Refreshes song info and lyrics when the button is clicked"""
        self.song, self.artist = self.fetch_song_info()
        self.parsed_lyrics, self.timestamps = self.fetch_lyrics()

        # Update UI song title
        self.song_label.setText(f"Now Playing: {self.song} by {self.artist}")

        if not self.parsed_lyrics:
            self.lyrics_label.setText("Lyrics not found.")
        else:
            self.lyrics_label.setText("🎵...")  # Placeholder until lyrics sync

    def update_lyrics_loop(self):
        """Continuously updates the lyrics display based on the song's progress"""
        while True:
            self.update_lyrics_display()
            time.sleep(1)  # Update every second

    def update_lyrics_display(self):
        """Updates lyrics dynamically based on the song's progress"""
        if self.full_lyrics_mode or not self.parsed_lyrics:
            return  # Do not update in full lyrics mode

        self.song, self.artist = self.fetch_song_info()
        self.song_label.setText(f"Now Playing: {self.song} by {self.artist}")

        if not self.timestamps:
            return

        # Find the closest timestamp to the current progress
        closest_time = min(self.timestamps, key=lambda t: abs(convert_to_seconds(t) - self.current_progress))

        # Show "🎵..." if the timestamp hasn't been reached yet
        if convert_to_seconds(closest_time) > self.current_progress:
            self.lyrics_label.setText("🎵...")
        else:
            self.lyrics_label.setText(self.parsed_lyrics.get(closest_time, "Lyrics syncing..."))

    def toggle_full_lyrics(self):
        """Toggles between full lyrics and synced lyrics mode"""
        self.full_lyrics_mode = not self.full_lyrics_mode

        if self.full_lyrics_mode:
            # Show full lyrics
            full_lyrics_text = "\n".join(f"[{time}] {line}" for time, line in self.parsed_lyrics.items())
            self.lyrics_label.setText(full_lyrics_text)
            self.toggle_button.setText("Show Synced Lyrics")
        else:
            # Return to synced mode
            self.refresh_lyrics()
            self.toggle_button.setText("Show Full Lyrics")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())
