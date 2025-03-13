import time
import torch
from transformers import pipeline
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
import yake
from sentence_transformers import SentenceTransformer, util
import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QPoint, QTimer, QRect
import sys
import random
from emoji_generator import extract_lyrics_themes

class DraggableEmoji(QLabel):
    def __init__(self, parent, emoji):
        super().__init__(parent)
        self.emoji = emoji
        self.setText(emoji)
        self.setStyleSheet("font-size: 60px; background-color: transparent;")
        self.setGeometry(random.randint(0, 900), random.randint(0, 700), 100, 100)
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
        self.setWindowTitle("Spotify Lyrics Fetcher")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: white;")
        self.active_emojis = []
        self.lyrics_dict = {}
        self.scrapbook_area = (100, 100, 800, 600)

        layout = QVBoxLayout()

        self.bg_label = QLabel(self)
        pixmap = QPixmap("/Users/PearlCxndie_1/Documents/GitHub/PComp-Sprint/SpotifyAPI-Scrapbook/scrapbook.png")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.bg_label)

        self.lyrics_label = QLabel("Waiting for lyrics...")
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setStyleSheet("font-size: 40px; font-weight: bold; color: black;")
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lyrics_label)

        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh Lyrics")
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        self.refresh_button.setStyleSheet("font-size: 18px; padding: 10px 20px;color: black;")
        button_layout.addWidget(self.refresh_button)

        self.toggle_button = QPushButton("Show Full Lyrics")
        self.toggle_button.clicked.connect(self.show_full_lyrics)
        self.toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px;color: black;")
        button_layout.addWidget(self.toggle_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.lyrics_timer = QTimer()
        self.lyrics_timer.timeout.connect(self.update_real_time_lyrics)
        self.lyrics_timer.start(2000)

        self.emoji_timer = QTimer()
        self.emoji_timer.timeout.connect(self.auto_generate_emoji)
        self.emoji_timer.start(10000)

    def refresh_lyrics(self):
        song, artist, _ = get_current_song()
        self.lyrics_dict, _ = get_lyrics(song, artist)
        if self.lyrics_dict:
            self.lyrics_label.setText("🎵...")
        else:
            self.lyrics_label.setText("Lyrics not found.")

    def update_real_time_lyrics(self):
        if self.lyrics_dict:
            current_progress = get_current_song()[2]
            if self.lyrics_dict:
                closest_time = min(self.lyrics_dict, key=lambda t: abs(convert_to_seconds(t) - current_progress))
                self.lyrics_label.setText(self.lyrics_dict[closest_time])

    def show_full_lyrics(self):
        if self.lyrics_dict:
            full_lyrics = "\n".join(self.lyrics_dict.values())
            self.lyrics_label.setText(full_lyrics)
        else:
            self.lyrics_label.setText("Lyrics not found.")

    def auto_generate_emoji(self):
        sample_lyrics = self.lyrics_label.text()
        _, _, emojis = extract_lyrics_themes(sample_lyrics)
        if emojis and emojis != ["❓"]:
            print(f"💜 Auto-generated Emojis: {emojis}")
            for emoji_char in emojis:
                self.spawn_emoji(emoji_char)

    def spawn_emoji(self, emoji):
        x, y = random.randint(0, 900), random.randint(0, 700)
        if not (self.scrapbook_area[0] <= x <= self.scrapbook_area[2] and self.scrapbook_area[1] <= y <= self.scrapbook_area[3]):
            draggable_emoji = DraggableEmoji(self, emoji)
            draggable_emoji.setGeometry(x, y, 100, 100)
            draggable_emoji.show()
            self.active_emojis.append(draggable_emoji)

        self.active_emojis = [e for e in self.active_emojis if e.geometry().intersects(QRect(*self.scrapbook_area)) or len(self.active_emojis) <= 10]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())