import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QHBoxLayout, QSlider, QSizeGrip
)
from PyQt6.QtGui import QPixmap, QMouseEvent, QFont
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, QPropertyAnimation
from rembg import remove
from emoji_generator import extract_lyrics_themes
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds

class ResizableDraggableImage(QLabel):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        if self.pixmap.isNull():
            print(f"Failed to load image from {image_path}")
        self.setPixmap(self.pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        self.setStyleSheet("background-color: transparent; border: 1px dashed black;")
        self.setGeometry(50, 50, 100, 100)
        self.dragging = False
        self.offset = QPoint()
        self.show_border = True  # Toggle for dashed border

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

    def toggle_border(self):
        """Toggle the dashed border on and off."""
        self.show_border = not self.show_border
        if self.show_border:
            self.setStyleSheet("background-color: transparent; border: 1px dashed black;")
        else:
            self.setStyleSheet("background-color: transparent; border: none;")

    def resize_image(self, size):
        """Resize the image to the specified size."""
        self.setPixmap(self.pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio))
        self.setFixedSize(size, size)

class DraggableEmoji(QLabel):
    def __init__(self, parent, emoji, size):
        super().__init__(parent)
        self.setText(emoji)
        self.setFont(QFont('Arial', size))
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(random.randint(100, 800), random.randint(100, 600), size, size)
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
        self.setWindowTitle("Spotify Lyrics Fetcher with Image Upload")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: white;")
        self.active_emojis = []
        self.lyrics_dict = {}
        self.scrapbook_area = QRect(100, 100, 800, 600)
        self.emoji_size = 50  # Default emoji size
        self.image_size = 100  # Default image size
        self.emoji_enabled = False

        # Main layout
        main_layout = QHBoxLayout()

        # Left side layout for sliders
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Slider for emoji size
        self.emoji_slider = QSlider(Qt.Orientation.Vertical)
        self.emoji_slider.setMinimum(20)
        self.emoji_slider.setMaximum(200)
        self.emoji_slider.setValue(self.emoji_size)
        self.emoji_slider.valueChanged.connect(self.update_emoji_size)
        left_layout.addWidget(QLabel("Emoji Size"))
        left_layout.addWidget(self.emoji_slider)

        # Slider for image size
        self.image_slider = QSlider(Qt.Orientation.Vertical)
        self.image_slider.setMinimum(20)
        self.image_slider.setMaximum(200)
        self.image_slider.setValue(self.image_size)
        self.image_slider.valueChanged.connect(self.update_image_size)
        left_layout.addWidget(QLabel("Image Size"))
        left_layout.addWidget(self.image_slider)

        # Add left layout to main layout
        main_layout.addLayout(left_layout)

        # Right side layout for the rest of the UI
        right_layout = QVBoxLayout()

        # Emoji Toggle Button
        self.emoji_toggle_button = QPushButton("Emojis: OFF")
        self.emoji_toggle_button.clicked.connect(self.toggle_emojis)
        self.emoji_toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px; color: black;")
        right_layout.addWidget(self.emoji_toggle_button)

        # Upload Button
        self.upload_button = QPushButton("Upload Picture")
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_button.setStyleSheet("font-size: 18px; padding: 10px 20px; color: black;")
        right_layout.addWidget(self.upload_button)

        # Background Image
        self.bg_label = QLabel(self)
        pixmap = QPixmap("/Users/PearlCxndie_1/Documents/GitHub/PComp-Sprint/SpotifyAPI-Scrapbook/scrapbook.png")
        if pixmap.isNull():
            print("Failed to load background image")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.bg_label)

        # Lyrics Label
        self.lyrics_label = QLabel("Waiting for lyrics...")
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setStyleSheet("font-size: 40px; font-weight: bold; color: black;")
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.lyrics_label)

        # Buttons for Lyrics Control
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Lyrics")
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        self.refresh_button.setStyleSheet("font-size: 18px; padding: 10px 20px;color: black;")
        button_layout.addWidget(self.refresh_button)

        self.toggle_button = QPushButton("Show Full Lyrics")
        self.toggle_button.clicked.connect(self.show_full_lyrics)
        self.toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px;color: black;")
        button_layout.addWidget(self.toggle_button)

        right_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # Timers
        self.lyrics_timer = QTimer()
        self.lyrics_timer.timeout.connect(self.update_real_time_lyrics)
        self.lyrics_timer.start(2000)

        self.emoji_timer = QTimer()
        self.emoji_timer.timeout.connect(self.auto_generate_emoji)
        self.emoji_timer.start(10000)  # Emoji generation every 10 seconds

    def toggle_emojis(self):
        self.emoji_enabled = not self.emoji_enabled
        if self.emoji_enabled:
            self.emoji_toggle_button.setText("Emojis: ON")
            self.emoji_toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px; color: black;")
        else:
            self.emoji_toggle_button.setText("Emojis: OFF")
            self.emoji_toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px; color: black;")
        self.emoji_timer.start(10000)  # Emoji generation every 10 seconds

    def upload_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.xpm *.jpg *.jpeg)")

        if file_path:
            output_path = self.remove_background(file_path)
            draggable_image = ResizableDraggableImage(self, output_path)
            draggable_image.resize_image(self.image_size)
            draggable_image.show()

    def remove_background(self, image_path):
        output_path = os.path.join(os.path.dirname(image_path), "removed_bg.png")
        with open(image_path, "rb") as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)
            with open(output_path, "wb") as output_file:
                output_file.write(output_data)
        return output_path

    def toggle_emojis(self):
        self.emoji_enabled = not self.emoji_enabled
        if self.emoji_enabled:
            self.emoji_toggle_button.setText("Emojis: ON")
            self.emoji_toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px; color: black;")
        else:
            self.emoji_toggle_button.setText("Emojis: OFF")
            self.emoji_toggle_button.setStyleSheet("font-size: 18px; padding: 10px 20px; color: black;")
        
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
        if len(self.active_emojis) >= 15:
            old_emoji = self.active_emojis.pop(0)
            old_emoji.deleteLater()

        draggable_emoji = DraggableEmoji(self, emoji, self.emoji_size)
        draggable_emoji.show()
        self.active_emojis.append(draggable_emoji)

    def update_emoji_size(self, value):
        """Update the size of emojis based on the slider value."""
        self.emoji_size = value
        for emoji in self.active_emojis:
            emoji.setFont(QFont('Arial', self.emoji_size))
            emoji.setFixedSize(self.emoji_size, self.emoji_size)

    def update_image_size(self, value):
        """Update the size of images based on the slider value."""
        self.image_size = value
        for child in self.children():
            if isinstance(child, ResizableDraggableImage):
                child.resize_image(self.image_size)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())