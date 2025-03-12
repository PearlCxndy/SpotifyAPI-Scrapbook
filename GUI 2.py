from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog
from PyQt6.QtGui import QPixmap, QMouseEvent, QColor, QPainter
from PyQt6.QtCore import Qt, QPoint, QRect
import sys
import time
import threading
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds

class FullLyricsPopup(QDialog):
    def __init__(self, song, artist, lyrics_text):
        super().__init__()
        self.setWindowTitle(f"Full Lyrics - {song} by {artist}")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()

        # Song and artist title
        title_label = QLabel(f"{song} by {artist}")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Full lyrics text
        self.lyrics_label = QLabel(lyrics_text)
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setStyleSheet("font-size: 18px; color: black;")
        layout.addWidget(self.lyrics_label)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("font-size: 16px; padding: 10px; color: black;")
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

class DraggableSquare(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(300, 300, 200, 200)
        self.setStyleSheet("background-color: black;")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

class LyricsApp(QWidget):
    def __init__(self):
        super().__init__()

        self.song = "Fetching song..."
        self.artist = "Loading artist..."
        self.current_progress = 0
        self.parsed_lyrics = {}
        self.timestamps = []

        self.initUI()
        self.refresh_lyrics()

        self.lyrics_updater = threading.Thread(target=self.update_lyrics_loop, daemon=True)
        self.lyrics_updater.start()

    def initUI(self):
        self.setWindowTitle("Spotify Lyrics Fetcher")
        self.showFullScreen()
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()

        # Background image scaled to full screen
        self.bg_label = QLabel(self)
        pixmap = QPixmap("/Users/PearlCxndie_1/Documents/GitHub/PComp-Sprint/SpotifyAPI-Scrapbook/scrapbook.png")
        screen_geometry = QApplication.primaryScreen().geometry()
        scaled_pixmap = pixmap.scaled(
            int(screen_geometry.width() * 0.95),
            int(screen_geometry.height() * 0.85),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.bg_label.setPixmap(scaled_pixmap)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.bg_label)

        # Lyrics Label
        self.lyrics_label = QLabel("Waiting for lyrics...")
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setStyleSheet("font-size: 40px; font-weight: bold; color: black;")
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lyrics_label)

        # Draggable Square
        self.square = DraggableSquare(self)
        self.square.show()

        # Buttons layout
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh Lyrics")
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        self.refresh_button.setStyleSheet("font-size: 18px; color: black; padding: 10px 20px;")
        button_layout.addWidget(self.refresh_button)

        self.toggle_button = QPushButton("Show Full Lyrics")
        self.toggle_button.clicked.connect(self.toggle_full_lyrics)
        self.toggle_button.setStyleSheet("font-size: 18px; color: black; padding: 10px 20px;")
        button_layout.addWidget(self.toggle_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def fetch_song_info(self):
        try:
            song, artist, progress = get_current_song()
            if song and artist:
                self.current_progress = progress
                return song, artist
        except Exception as e:
            print(f"Error fetching song info: {e}")
        return "No song playing", "Unknown Artist"

    def fetch_lyrics(self):
        if self.song == "No song playing":
            return {}, []

        try:
            lyrics_dict, timestamps_list = get_lyrics(self.song, self.artist)
            print("✅ Lyrics successfully fetched as dictionary.")
            return lyrics_dict, timestamps_list
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return {}, []

    def refresh_lyrics(self):
        self.song, self.artist = self.fetch_song_info()
        self.parsed_lyrics, self.timestamps = self.fetch_lyrics()

        if not self.parsed_lyrics:
            self.lyrics_label.setText("Lyrics not found.")
        else:
            self.lyrics_label.setText("🎵...")

    def update_lyrics_loop(self):
        while True:
            self.update_lyrics_display()
            time.sleep(1)

    def update_lyrics_display(self):
        if not self.parsed_lyrics or not self.timestamps:
            return

        closest_time = min(self.timestamps, key=lambda t: abs(convert_to_seconds(t) - self.current_progress))
        if convert_to_seconds(closest_time) > self.current_progress:
            self.lyrics_label.setText("🎵...")
        else:
            self.lyrics_label.setText(self.parsed_lyrics.get(closest_time, "Lyrics syncing..."))

    def toggle_full_lyrics(self):
        """Display full lyrics in a new pop-up window."""
        if not self.parsed_lyrics:
            self.lyrics_label.setText("Lyrics not found.")
            return

        full_lyrics_text = "\n".join(f"[{time}] {line}" for time, line in self.parsed_lyrics.items())
        if not full_lyrics_text.strip():
            full_lyrics_text = "Lyrics not available or syncing..."

        popup = FullLyricsPopup(self.song, self.artist, full_lyrics_text)
        popup.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())
