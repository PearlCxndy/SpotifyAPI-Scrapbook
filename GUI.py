from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import sys
from spotifylyrics import get_current_song  # Import your Spotify function
from LyricsFetcher import get_lyrics  # New SyncedLyrics import

class LyricsApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize values with default fallback
        self.song, self.artist = "Fetching song...", "Loading artist..."
        self.lyrics = "Loading lyrics..."

        self.initUI()
        self.refresh_lyrics()  # Fetch song & lyrics on startup

    def initUI(self):
        """Initialize the UI layout"""
        self.setWindowTitle("Spotify Lyrics Fetcher")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Song title display
        self.song_label = QLabel(f"Now Playing: {self.song} by {self.artist}")
        self.song_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.song_label)

        # Lyrics display
        self.lyrics_label = QLabel(self.lyrics)
        self.lyrics_label.setWordWrap(True)
        layout.addWidget(self.lyrics_label)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Lyrics")
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def fetch_song_info(self):
        """Fetch the currently playing song from Spotify"""
        try:
            song, artist = get_current_song()
            if song and artist:
                return song, artist
        except Exception as e:
            print(f"Error fetching song info: {e}")

        return "No song playing", "Unknown Artist"  # Default fallback

    def fetch_lyrics(self, song, artist):
        """Fetch lyrics from Genius API"""
        if song == "No song playing":
            return "No lyrics available."
        
        try:
            lyrics = get_lyrics(song, artist)
            return lyrics if lyrics else "Lyrics not found."
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return "Error retrieving lyrics."

    def refresh_lyrics(self):
        """Refreshes song info and lyrics when the button is clicked"""
        self.song, self.artist = self.fetch_song_info()
        self.lyrics = self.fetch_lyrics(self.song, self.artist)

        # Update UI labels
        self.song_label.setText(f"Now Playing: {self.song} by {self.artist}")
        self.lyrics_label.setText(self.lyrics)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())
