from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import sys

class LyricsApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Spotify Lyrics Fetcher")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.song_label = QLabel(f"Now Playing: {song} by {artist}")
        self.song_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.song_label)

        self.lyrics_label = QLabel(lyrics)
        self.lyrics_label.setWordWrap(True)
        layout.addWidget(self.lyrics_label)

        self.refresh_button = QPushButton("Refresh Lyrics")
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def refresh_lyrics(self):
        global song, artist, lyrics
        song, artist = get_current_song()
        if song and artist:
            lyrics = get_lyrics(song, artist)
            self.song_label.setText(f"Now Playing: {song} by {artist}")
            self.lyrics_label.setText(lyrics)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())
