import sys
import os
import random
from io import BytesIO
import cv2

from PIL import Image, ImageQt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QHBoxLayout, QSlider, QStackedLayout, QLineEdit, QInputDialog, QDialog
)



from PyQt6.QtGui import QPixmap, QMouseEvent, QFont, QFontDatabase, QImage, QColor,QFontDatabase, QImage, QPainter
from PyQt6.QtCore import Qt, QPoint, QTimer, QRect

from rembg import remove
from emoji_generator import extract_lyrics_themes
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
from sticker import generate_ai_image, remove_image_background
# from spotifyalbum import fetch_current_track_data
from drawingcanvas import HandDrawingCanvas



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
        self.parent = parent  # Reference to the parent (LyricsApp)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()
            self.parent.set_selected_item(self)  # Notify parent that this item is selected

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

    def remove_background(self, image_path):
            output_path = os.path.join(os.path.dirname(image_path), "removed_bg.png")
            with open(image_path, "rb") as input_file:
                input_data = input_file.read()
                output_data = remove(input_data)
                with open(output_path, "wb") as output_file:
                    output_file.write(output_data)
            return output_path

class DraggableAISticker(QLabel):
    def __init__(self, parent, prompt):
        super().__init__(parent)
        self.prompt = prompt
        self.sticker_image = self.generate_sticker(prompt)  # Get the PIL.Image object
        if self.sticker_image:
            self.pixmap = self._pil_to_pixmap(self.sticker_image)  # Convert PIL.Image to QPixmap
            if self.pixmap.isNull():
                print(f"Failed to load sticker from generated image.")
            else:
                self.setPixmap(self.pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                self.setStyleSheet("background-color: transparent; border: 1px dashed black;")
                self.setGeometry(50, 50, 100, 100)
                self.dragging = False
                self.offset = QPoint()
                self.show_border = True  # Toggle for dashed border
                self.parent = parent  # Reference to the parent (LyricsApp)
        else:
            print("Failed to generate AI sticker.")

    def generate_sticker(self, prompt):
        """Generates an AI sticker and returns the PIL.Image object."""
        # Generate AI image
        ai_image = generate_ai_image(prompt)
        if ai_image:
            # Remove background
            bg_removed_image = remove_image_background(ai_image)
            return bg_removed_image  # Return the PIL.Image object
        return None

    def _pil_to_pixmap(self, pil_image):
        """Converts a PIL.Image to a QPixmap."""
        from PIL.ImageQt import ImageQt
        from PyQt6.QtGui import QPixmap
        qimage = ImageQt(pil_image)
        return QPixmap.fromImage(qimage)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()
            self.parent.set_selected_item(self)  # Notify parent that this item is selected

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

    def resize_sticker(self, size):
        """Resize the sticker to the specified size."""
        if hasattr(self, 'pixmap'):
            self.setPixmap(self.pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio))
            self.setFixedSize(size, size)

    def generate_sticker(self, prompt):
        """Generates an AI sticker and saves it to the output directory."""
        output_dir = "generated_stickers"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{prompt.replace(' ', '_')}.png")

        # Generate AI image
        ai_image = generate_ai_image(prompt)
        if ai_image:
            # Remove background
            bg_removed_image = remove_image_background(ai_image)
            bg_removed_image.save(file_path)
            return file_path
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()
            self.parent.set_selected_item(self)  # Notify parent that this item is selected

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

    def resize_sticker(self, size):
        """Resize the sticker to the specified size."""
        if hasattr(self, 'pixmap'):
            self.setPixmap(self.pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio))
            self.setFixedSize(size, size)

class DraggableEmoji(QLabel):
    def __init__(self, parent, emoji, size):
        super().__init__(parent)
        self.setText(emoji)
        self.setFont(QFont('Arial', size))  # Use custom font
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(random.randint(100, 800), random.randint(100, 600), size, size)
        self.dragging = False
        self.offset = QPoint()
        self.parent = parent  # Reference to the parent (LyricsApp)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.parent.set_selected_item(self) 

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
class DraggableText(QLabel):
    def __init__(self, parent, text, font_size):
        super().__init__(parent)
        self.setText(text)
        self.setFont(QFont(parent.custom_font, font_size))
        self.setStyleSheet("background-color: transparent; color: black;")
        self.setGeometry(random.randint(100, 800), random.randint(100, 600), 200, 50)
        self.dragging = False
        self.offset = QPoint()
        self.parent = parent  # Reference to the parent (LyricsApp)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.parent.set_selected_item(self)  # Notify parent that this item is selected

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

    def resize_text(self, size):
        """Resize the text to the specified size."""
        self.setFont(QFont(self.parent.custom_font, size))
        self.setFixedSize(self.fontMetrics().boundingRect(self.text()).width(), self.fontMetrics().height())

class HandDrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def process_frame(self, frame):
        """Process the webcam frame (e.g., apply drawing or effects)."""
        # Example: Draw a red rectangle on the frame
        cv2.rectangle(frame, (50, 50), (200, 200), (0, 0, 255), 2)
        return frame

class LyricsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Lyrics Fetcher with Image Upload and AI Stickers")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.active_emojis = []
        self.active_stickers = []
        self.lyrics_dict = {}
        self.scrapbook_area = QRect(100, 100, 800, 600)
        self.emoji_size = 50
        self.image_size = 100
        self.sticker_size = 100
        self.emoji_enabled = False
        self.sticker_enabled = False
        self.selected_item = None

        # Load custom font
        font_path = "/Users/PearlCxndie_1/Documents/GitHub/PComp-Sprint/SpotifyAPI-Scrapbook/Remingtoned Type.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Failed to load custom font. Falling back to Arial.")
            self.custom_font = "Arial"
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Available font families: {font_families}")
            self.custom_font = font_families[0] if font_families else "Arial"
            print(f"Custom font loaded: {self.custom_font}")

        # Get screen dimensions
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.resize(screen_geometry.width(), screen_geometry.height())

        # Main layout
        main_layout = QHBoxLayout()

        # Left side layout for sliders (combined and compact)
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        # Label for combined sliders
        resize_label = QLabel("Resize Controls")
        resize_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        self.left_layout.addWidget(resize_label)


        self.stacked_layout = QStackedLayout()

        # Slider for emoji size
        self.emoji_slider = QSlider(Qt.Orientation.Vertical)
        self.emoji_slider.setMinimum(20)
        self.emoji_slider.setMaximum(200)
        self.emoji_slider.setValue(self.emoji_size)
        self.emoji_slider.valueChanged.connect(self.update_selected_item_size)
        self.emoji_slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: white;
                width: 10px;
                border-radius: 5px;
            }
            QSlider::handle:vertical {
                background: black;
                width: 20px;
                height: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)
        emoji_slider_widget = QWidget()
        emoji_slider_layout = QVBoxLayout()
        emoji_slider_layout.addWidget(QLabel("Emoji Size"))
        emoji_slider_layout.addWidget(self.emoji_slider)
        emoji_slider_widget.setLayout(emoji_slider_layout)
        self.left_layout.addWidget(emoji_slider_widget)

        # Slider for image size
        self.image_slider = QSlider(Qt.Orientation.Vertical)
        self.image_slider.setMinimum(20)
        self.image_slider.setMaximum(200)
        self.image_slider.setValue(self.image_size)
        self.image_slider.valueChanged.connect(self.update_selected_item_size)
        self.image_slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: white;
                width: 10px;
                border-radius: 5px;
            }
            QSlider::handle:vertical {
                background: black;
                width: 20px;
                height: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)
        image_slider_widget = QWidget()
        image_slider_layout = QVBoxLayout()
        image_slider_layout.addWidget(QLabel("Image Size"))
        image_slider_layout.addWidget(self.image_slider)
        image_slider_widget.setLayout(image_slider_layout)
        self.left_layout.addWidget(image_slider_widget)

        # Slider for sticker size
        self.sticker_slider = QSlider(Qt.Orientation.Vertical)
        self.sticker_slider.setMinimum(20)
        self.sticker_slider.setMaximum(200)
        self.sticker_slider.setValue(self.sticker_size)
        self.sticker_slider.valueChanged.connect(self.update_selected_item_size)
        self.sticker_slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: white;
                width: 10px;
                border-radius: 5px;
            }
            QSlider::handle:vertical {
                background: black;
                width: 20px;
                height: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)
        sticker_slider_widget = QWidget()
        sticker_slider_layout = QVBoxLayout()
        sticker_slider_layout.addWidget(QLabel("Sticker Size"))
        sticker_slider_layout.addWidget(self.sticker_slider)
        sticker_slider_widget.setLayout(sticker_slider_layout)
        self.left_layout.addWidget(sticker_slider_widget)

        # Add stacked layout to left layout
        self.left_layout.addLayout(self.stacked_layout)

        # Add left layout to main layout (hidden by default)
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(self.left_layout)
        self.sidebar_widget.setFixedWidth(120)
        self.sidebar_widget.hide()
        main_layout.addWidget(self.sidebar_widget)

        # Right side layout for the rest of the UI
        right_layout = QVBoxLayout()

        # Background Image
        self.bg_label = QLabel(self)
        pixmap = QPixmap("/Users/PearlCxndie_1/Documents/GitHub/PComp-Sprint/SpotifyAPI-Scrapbook/scrapbook.png")
        if pixmap.isNull():
            print("Failed to load background image")

        # Scale the image to 10% larger
        original_width = pixmap.width()
        original_height = pixmap.height()
        scaled_width = int(original_width * 0.8)
        scaled_height = int(original_height * 0.8)
        scaled_pixmap = pixmap.scaled(
            scaled_width, scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Set the scaled pixmap to the label
        self.bg_label.setPixmap(scaled_pixmap)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg_label.setFixedSize(scaled_width, scaled_height)

        # Center the background image on the screen
        window_width = self.width()
        window_height = self.height()
        x = (window_width - scaled_width) // 2
        y = (window_height - scaled_height) // 2
        self.bg_label.move(x, y)

        # --- Create a container widget for the buttons ---
        self.button_container = QWidget(self)
        self.button_container.setFixedSize(200, 200)
        self.button_container.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.button_container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Button layout
        self.button_layout = QVBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_container.setLayout(self.button_layout)

        # Position the button container at the top-right corner
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        button_x = screen_geometry.width() - self.button_container.width() - 20
        button_y = 20
        self.button_container.move(button_x, button_y)

        # --- Lyrics Label ---
        self.lyrics_label = QLabel("Waiting for lyrics...", self)
        self.lyrics_label.setWordWrap(True)  # Enable word wrap for long lyrics
        self.lyrics_label.setStyleSheet("font-size: 40px; font-weight: bold; color: white;")
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the lyrics label to the right layout
        right_layout.addWidget(self.lyrics_label)


        # Buttons for Lyrics Control
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Lyrics", self)
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        self.refresh_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        button_layout.addWidget(self.refresh_button)

        self.toggle_button = QPushButton("Show Full Lyrics", self)
        self.toggle_button.clicked.connect(self.show_full_lyrics)
        self.toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        button_layout.addWidget(self.toggle_button)

        right_layout.addLayout(button_layout)

        # Add buttons to the container
        self.emoji_toggle_button = QPushButton("Emojis: OFF", self.button_container)
        self.emoji_toggle_button.clicked.connect(self.toggle_emojis)
        self.emoji_toggle_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.emoji_toggle_button)

        self.sticker_toggle_button = QPushButton("AI Stickers: OFF", self.button_container)
        self.sticker_toggle_button.clicked.connect(self.toggle_stickers)
        self.sticker_toggle_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.sticker_toggle_button)

        self.upload_button = QPushButton("Upload Picture", self.button_container)
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.upload_button)

        self.add_text_button = QPushButton("Add Text", self.button_container)
        self.add_text_button.clicked.connect(self.add_text)
        self.add_text_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.add_text_button)

        # Ensure the buttons are clickable
        self.button_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.emoji_toggle_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.sticker_toggle_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.upload_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.add_text_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Raise the buttons to ensure they are on top
        self.button_container.raise_()
        self.emoji_toggle_button.raise_()
        self.sticker_toggle_button.raise_()
        self.upload_button.raise_()
        self.add_text_button.raise_()

        # Initialize the drawing canvas
        self.drawing_canvas = HandDrawingCanvas(600, 600)

         # --- Create Webcam Label for Display ---
        self.webcam_label = QLabel(self)
        self.webcam_label.setFixedSize(300, 250)  # Set a fixed size for the webcam feed
        self.webcam_label.setStyleSheet("border: 2px solid black; background-color: black;")

        # Position the webcam label at the far right side of the screen
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        webcam_x = (screen_geometry.width() - self.webcam_label.width()) - 50  # Align to the right
        webcam_y = (screen_geometry.height() - self.webcam_label.height()) - 100  # Align to the bottom
        self.webcam_label.move(webcam_x, webcam_y)
        self.webcam_label.raise_()  # Ensure it appears on top of other widgets

        # Initialize Webcam
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("⚠️ Webcam not accessible!")

        # Timer to update webcam feed
        self.webcam_timer = QTimer()
        self.webcam_timer.timeout.connect(self.update_webcam_feed)
        self.webcam_timer.start(30)

        # Add the right layout to the main layout
        main_layout.addLayout(right_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

        # Timers
        self.lyrics_timer = QTimer()
        self.lyrics_timer.timeout.connect(self.update_real_time_lyrics)
        self.lyrics_timer.start(2000)

        self.emoji_timer = QTimer()
        self.emoji_timer.timeout.connect(self.auto_generate_emoji)
        self.emoji_timer.start(10000)

        self.sticker_timer = QTimer()
        self.sticker_timer.timeout.connect(self.auto_generate_sticker)
        self.sticker_timer.start(15000)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            print(f"Mouse press at: {event.pos()}")
        return super().eventFilter(obj, event)

        # Install event filter on the main window
        self.installEventFilter(self)

    def update_webcam_feed(self):
        """Capture, process, and display the webcam feed."""
        ret, frame = self.capture.read()
        if ret:
            # Resize the frame to match the webcam_label size (400x300)
            frame = cv2.resize(frame, (self.webcam_label.width(), self.webcam_label.height()))

            # Process the frame through the drawing canvas (if needed)
            processed_frame = self.drawing_canvas.process_frame(frame)

            # Convert the processed frame to RGB format
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = processed_frame.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(processed_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.webcam_label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))

    def add_text(self):
        """Open a dialog to input text and add it to the canvas."""
        text, ok = QInputDialog.getText(self, 'Add Text', 'Enter your text:')
        if ok and text:
            draggable_text = DraggableText(self, text, 30)  # Initial font size of 30
            draggable_text.show()
            self.set_selected_item(draggable_text)

    def toggle_emojis(self):
        """Toggle emoji generation on and off."""
        self.emoji_enabled = not self.emoji_enabled
        if self.emoji_enabled:
            self.emoji_toggle_button.setText("Emojis: ON")
            self.emoji_toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        else:
            self.emoji_toggle_button.setText("Emojis: OFF")
            self.emoji_toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")

    def toggle_stickers(self):
        """Toggle AI sticker generation on and off."""
        self.sticker_enabled = not self.sticker_enabled
        if self.sticker_enabled:
            self.sticker_toggle_button.setText("AI Stickers: ON")
            self.sticker_toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        else:
            self.sticker_toggle_button.setText("AI Stickers: OFF")
            self.sticker_toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")

    def auto_generate_sticker(self):
        """Automatically generate AI stickers based on lyrics."""
        if not self.sticker_enabled:
            return

        sample_lyrics = self.lyrics_label.text()
        if sample_lyrics and sample_lyrics != "Waiting for lyrics...":
            ai_sticker = DraggableAISticker(self, sample_lyrics)
            ai_sticker.show()
            self.active_stickers.append(ai_sticker)
            self.set_selected_item(ai_sticker)

    def set_selected_item(self, item):
        """Set the currently selected item and show the sidebar."""
        self.selected_item = item
        self.sidebar_widget.show()

        # Update sliders based on the selected item
        if isinstance(item, DraggableEmoji):
            self.stacked_layout.setCurrentIndex(0)  # Show emoji slider
            self.emoji_slider.setValue(item.font().pointSize())
        elif isinstance(item, ResizableDraggableImage):
            self.stacked_layout.setCurrentIndex(1)  # Show image slider
            self.image_slider.setValue(item.width())
        elif isinstance(item, DraggableText):
            self.stacked_layout.setCurrentIndex(0)  # Show emoji slider (reusing for text size)
            self.emoji_slider.setValue(item.font().pointSize())
        elif isinstance(item, DraggableAISticker):
            self.stacked_layout.setCurrentIndex(2)  # Show sticker slider
            self.sticker_slider.setValue(item.width())

    def update_selected_item_size(self):
        """Update the size of the selected item based on the slider values."""
        if self.selected_item:
            try:
                if isinstance(self.selected_item, DraggableEmoji):
                    new_size = self.emoji_slider.value()
                    self.selected_item.setFont(QFont(self.custom_font, new_size))
                    self.selected_item.setFixedSize(new_size, new_size)
                elif isinstance(self.selected_item, ResizableDraggableImage):
                    new_size = self.image_slider.value()
                    self.selected_item.resize_image(new_size)
                elif isinstance(self.selected_item, DraggableText):
                    new_size = self.emoji_slider.value()
                    self.selected_item.resize_text(new_size)
                elif isinstance(self.selected_item, DraggableAISticker):
                    new_size = self.sticker_slider.value()
                    self.selected_item.resize_sticker(new_size)
            except RuntimeError:
                # If the selected item has been deleted, clear the reference
                self.selected_item = None
                self.sidebar_widget.hide()
    def show_full_lyrics(self):
        """Show full lyrics in a popup window."""
        if self.lyrics_dict:
            full_lyrics = "\n".join(self.lyrics_dict.values())
        else:
            full_lyrics = "Lyrics not found."

        # Create the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Full Lyrics")
        dialog.setFixedSize(600, 400)

        # Add lyrics to the dialog
        lyrics_label = QLabel(full_lyrics, dialog)
        lyrics_label.setWordWrap(True)
        lyrics_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        lyrics_label.setStyleSheet("font-size: 16px; padding: 10px;")
        
        # Layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(lyrics_label)
        dialog.setLayout(layout)

        # Show the dialog
        dialog.exec()


    def refresh_lyrics(self):
        # Use the actual Spotify API to get the current song and artist
        song_info = get_current_song()

        # Ensure song_info is valid and contains necessary data
        if not song_info or not song_info[0] or not song_info[1]:
            self.lyrics_label.setText("No song playing or song data unavailable.")
            return

        song, artist = song_info[:2]

        # Avoid searching for placeholder song data
        if song == "No song playing" or artist == "Unknown Artist":
            self.lyrics_label.setText("No song playing or song data unavailable.")
            return

        # Fetch lyrics
        lyrics_result = get_lyrics(song, artist)

        # Check if lyrics were found
        if lyrics_result:
            self.lyrics_dict, _ = lyrics_result
            combined_lyrics = "\n".join(self.lyrics_dict.values()) if self.lyrics_dict else "No lyrics available."
            self.lyrics_label.setText(combined_lyrics)
        else:
            self.lyrics_dict = {}
            self.lyrics_label.setText("No lyrics available.")



    def update_real_time_lyrics(self):
        # Check if lyrics dictionary is populated
        if not self.lyrics_dict:
            return

        # Get current song progress from Spotify
        current_song = get_current_song()

        # Validate song information
        if not current_song or current_song[0] == "No song playing":
            return

        current_progress = current_song[2]

        # Convert and validate times
        valid_times = {
            t: convert_to_seconds(t)
            for t in self.lyrics_dict
            if convert_to_seconds(t) is not None
        }

        if not valid_times:
            self.lyrics_label.setText("No valid timestamps found.")
            return

        # Find the closest time and update the lyrics label
        closest_time = min(valid_times, key=lambda t: abs(valid_times[t] - current_progress))
        self.lyrics_label.setText(self.lyrics_dict[closest_time])



    def auto_generate_emoji(self):
        if not self.emoji_enabled:  # Only generate emojis if emojis are enabled
            return

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
            if self.selected_item == old_emoji:  # Clear selected item if it was deleted
                self.selected_item = None
                self.sidebar_widget.hide()

        draggable_emoji = DraggableEmoji(self, emoji, self.emoji_size)
        draggable_emoji.show()
        self.active_emojis.append(draggable_emoji)

    def upload_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.xpm *.jpg *.jpeg)")

        if file_path:
            output_path = self.remove_background(file_path)
            draggable_image = ResizableDraggableImage(self, output_path)
            draggable_image.resize_image(self.image_size)
            draggable_image.show()


    def update_emoji_size(self, value):
        """Update the size of emojis based on the slider value."""
        self.emoji_size = value
        for emoji in self.active_emojis:
            emoji.setFont(QFont(self.custom_font, self.emoji_size))  # Use custom font
            emoji.setFixedSize(self.emoji_size, self.emoji_size)

    def update_image_size(self, value):
        """Update the size of images based on the slider value."""
        self.image_size = value
        for child in self.children():
            if isinstance(child, ResizableDraggableImage):
                child.resize_image(self.image_size)

    def cleanup_resources(self):
        """Ensure webcam is released on app exit."""
        if self.capture.isOpened():
            self.capture.release()
            print("Webcam resource released.")

    def closeEvent(self, event):
        """Release webcam resources upon closing the window."""
        self.cleanup_resources()
        event.accept()
        
    def remove_background(self, image_path):
        """Removes the background from the given image and returns the output path."""
        output_path = os.path.join(os.path.dirname(image_path), "removed_bg.png")
        with open(image_path, "rb") as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)
            with open(output_path, "wb") as output_file:
                output_file.write(output_data)
        return output_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load custom font
    font_path = "/Users/PearlCxndie_1/Documents/GitHub/PComp-Sprint/SpotifyAPI-Scrapbook/Remingtoned Type.ttf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Failed to load custom font. Falling back to Arial.")
        custom_font = "Arial"
    else:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        print(f"Available font families: {font_families}")
        custom_font = font_families[0] if font_families else "Arial"
        print(f"Custom font loaded: {custom_font}")
    
    # Set the custom font globally
    app_font = QFont(custom_font, 12)  # Adjust size as needed
    app.setFont(app_font)
    
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())