import sys
import os
import random
from io import BytesIO
import cv2

from PIL import Image, ImageQt
from PyQt6.QtWidgets import (       
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QHBoxLayout, QSlider, QStackedLayout, QLineEdit, QInputDialog, QDialog, QColorDialog,QScrollArea,QGraphicsDropShadowEffect
)



from PyQt6.QtGui import QPixmap, QMouseEvent, QFont, QFontDatabase, QImage, QColor,QFontDatabase, QImage, QPainter
from PyQt6.QtCore import Qt, QPoint, QTimer, QRect

from rembg import remove
from emoji_generator import extract_lyrics_themes
from spotifylyrics import get_current_song
from LyricsFetcher import get_lyrics, convert_to_seconds
from sticker import generate_ai_image, remove_image_background
from spotifyalbum import fetch_current_track_data,set_canvas_bg_from_album, pick_canvas_bg_color
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
        self.show_border = True  
        self.parent = parent  

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()
            self.parent.set_selected_item(self) 

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

    def toggle_border(self):
        self.show_border = not self.show_border
        if self.show_border:
            self.setStyleSheet("background-color: transparent; border: 1px dashed black;")
        else:
            self.setStyleSheet("background-color: transparent; border: none;")


    def resize_image(self, size):
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
        self.sticker_image = self.generate_sticker(prompt) 
        if self.sticker_image:
            self.pixmap = self._pil_to_pixmap(self.sticker_image)  
            if self.pixmap.isNull():
                print(f"Failed to load sticker from generated image.")
            else:
                self.setPixmap(self.pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                self.setStyleSheet("background-color: transparent; border: 1px dashed black;")
                self.setGeometry(50, 50, 100, 100)
                self.dragging = False
                self.offset = QPoint()
                self.show_border = True 
                self.parent = parent  
        else:
            print("Failed to generate AI sticker.")

    def generate_sticker(self, prompt):
        ai_image = generate_ai_image(prompt)
        if ai_image:
            bg_removed_image = remove_image_background(ai_image)
            return bg_removed_image 
        return None

    def _pil_to_pixmap(self, pil_image):
        from PIL.ImageQt import ImageQt
        from PyQt6.QtGui import QPixmap
        qimage = ImageQt(pil_image)
        return QPixmap.fromImage(qimage)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()
            self.parent.set_selected_item(self)  

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

    def toggle_border(self):
        self.show_border = not self.show_border
        if self.show_border:
            self.setStyleSheet("background-color: transparent; border: 1px dashed black;")
        else:
            self.setStyleSheet("background-color: transparent; border: none;")

    def resize_sticker(self, size):
        if hasattr(self, 'pixmap'):
            self.setPixmap(self.pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio))
            self.setFixedSize(size, size)

    def generate_sticker(self, prompt):
        output_dir = "generated_stickers"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{prompt.replace(' ', '_')}.png")

        ai_image = generate_ai_image(prompt)
        if ai_image:
            bg_removed_image = remove_image_background(ai_image)
            bg_removed_image.save(file_path)
            return file_path
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.toggle_border()
            self.parent.set_selected_item(self)  

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

    def toggle_border(self):
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
        self.setFont(QFont('Arial', size))  
        self.setStyleSheet("background-color: transparent;")
        self.setGeometry(random.randint(100, 800), random.randint(100, 600), size, size)
        self.dragging = False
        self.offset = QPoint()
        self.parent = parent  

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
        self.parent = parent  

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

    def resize_text(self, size):
        self.setFont(QFont(self.parent.custom_font, size))
        self.setFixedSize(self.fontMetrics().boundingRect(self.text()).width(), self.fontMetrics().height())

class DraggableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.offset = QPoint()
        self.fixed_position = QPoint(400, 300) 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.raise_()  
    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)
            self.fixed_position = new_pos 
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False


class StrokeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        font = QFont("Arial", 30, QFont.Weight.Bold)
        painter.setFont(font)

        pen = QPen(QColor("black"), 4, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

        pen = QPen(QColor("white"), 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        
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

        font_path = "/Users/PearlCxndie_1/Documents/GitHub/SpotifyAPI-Scrapbook/Remingtoned Type.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Failed to load custom font. Falling back to Arial.")
            self.custom_font = "Arial"
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Available font families: {font_families}")
            self.custom_font = font_families[0] if font_families else "Arial"
            print(f"Custom font loaded: {self.custom_font}")

        
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)  

        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        right_layout = QVBoxLayout()
        self.main_layout.addLayout(right_layout)


        resize_label = QLabel("Resize Controls")
        resize_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        self.left_layout.addWidget(resize_label)


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

        self.stacked_layout = QStackedLayout()
        self.left_layout.addLayout(self.stacked_layout)

        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setLayout(self.left_layout)
        self.sidebar_widget.setFixedWidth(120)

        self.sidebar_widget.move(0, 0)
        self.sidebar_widget.raise_()  

        self.main_layout.insertWidget(0, self.sidebar_widget)  


  
        # Background Image
        self.bg_label = QLabel(self)
        pixmap = QPixmap("/Users/PearlCxndie_1/Documents/GitHub/SpotifyAPI-Scrapbook/scrapbook.png")
        original_width = pixmap.width()
        original_height = pixmap.height()
        scaled_width = int(original_width * 0.8)
        scaled_height = int(original_height * 0.8)
        scaled_pixmap = pixmap.scaled(
            scaled_width, scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.bg_label.setPixmap(scaled_pixmap)
        self.bg_label.setFixedSize(scaled_width, scaled_height)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        window_width = self.width()
        window_height = self.height()
        x = (window_width - scaled_width) // 2
        y = ((window_height - scaled_height) // 2) - 600
        self.bg_label.move(x, y)

        self.drawing_label = QLabel(self)
        self.drawing_label.setGeometry(self.bg_label.geometry())  
        self.drawing_label.setStyleSheet("background: transparent;") 
        self.drawing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bg_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.bg_label.raise_()
        self.auto_color_button = QPushButton("Auto BG Color", self)
        self.auto_color_button.setStyleSheet("""
            QPushButton {
                width: 120px;
                height: 40px;
                border-radius: 8px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.auto_color_button.move(350, 100)
        self.auto_color_button.clicked.connect(lambda: set_canvas_bg_from_album(self))
        self.auto_color_button.raise_() 

        self.manual_color_button = QPushButton("Pick BG Color", self)
        self.manual_color_button.setStyleSheet("""
            QPushButton {
                width: 120px;
                height: 40px;
                border-radius: 8px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
        """)
        self.manual_color_button.move(480, 100)
        self.manual_color_button.clicked.connect(lambda: pick_canvas_bg_color(self))
        self.manual_color_button.raise_()  


        self.bg_label.raise_()
        self.drawing_canvas = HandDrawingCanvas(self.drawing_label)


        self.button_container = QWidget(self)
        self.button_container.setFixedSize(200, 200)
        self.button_container.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.button_container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.button_layout = QVBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_container.setLayout(self.button_layout)

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        button_x = screen_geometry.width() - self.button_container.width() - 20
        button_y = 20
        self.button_container.move(button_x, button_y)

        self.lyrics_label = DraggableLabel(self)
        self.lyrics_label.setText("Waiting for lyrics...")
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: white;
        """)
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lyrics_label.setFixedSize(300, 100)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)           
        shadow.setColor(QColor('black'))   
        shadow.setOffset(0, 0)             
        self.lyrics_label.setGraphicsEffect(shadow)

        parent_width = self.width()
        parent_height = self.height()
        label_width = self.lyrics_label.width()
        label_height = self.lyrics_label.height()

        center_x = (parent_width - label_width) // 2
        center_y = (parent_height - label_height) // 2

        self.lyrics_label.move(center_x, center_y)
        self.lyrics_label.fixed_position = QPoint(center_x, center_y)
        self.lyrics_label.show()

        right_layout.addWidget(self.lyrics_label)
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Start ▶ / Refresh ↻ ", self)
        self.refresh_button.clicked.connect(self.refresh_lyrics)
        self.refresh_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        button_layout.setContentsMargins(0, 700, 0, 0) 
        button_layout.addWidget(self.refresh_button)

        self.toggle_button = QPushButton("Show Full Lyrics ↗", self)
        self.toggle_button.clicked.connect(self.show_full_lyrics)
        self.toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        button_layout.setContentsMargins(0, 700, 0, 0)  
        button_layout.addWidget(self.toggle_button)
        right_layout.addLayout(button_layout)

        self.emoji_toggle_button = QPushButton("Emojis: OFF", self.button_container)
        self.emoji_toggle_button.clicked.connect(self.toggle_emojis)
        self.emoji_toggle_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.emoji_toggle_button)

        self.sticker_toggle_button = QPushButton("AI Stickers: OFF", self.button_container)
        self.sticker_toggle_button.clicked.connect(self.toggle_stickers)
        self.sticker_toggle_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.sticker_toggle_button)

        self.upload_button = QPushButton("Upload Picture ⇣", self.button_container)
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.upload_button)

        self.add_text_button = QPushButton("Add Text", self.button_container)
        self.add_text_button.clicked.connect(self.add_text)
        self.add_text_button.setStyleSheet("background: white; font-size: 12px; padding: 5px; color: black;")
        self.button_layout.addWidget(self.add_text_button)


        self.button_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.emoji_toggle_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.sticker_toggle_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.upload_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.add_text_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)


        self.webcam_label = QLabel(self)
        self.webcam_label.setFixedSize(300, 250) 
        self.webcam_label.setStyleSheet("border: 2px solid black; background-color: black;")


        self.color_picker_container = QWidget(self)
        self.color_picker_container.setStyleSheet("background: rgba(255, 255, 255, 0.8); border-radius: 10px;")
        self.color_picker_container.setFixedSize(240, 120)
        self.color_picker_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.color_picker_container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


        color_layout = QVBoxLayout()


        self.color_picker_button = QPushButton("Pick Color", self.color_picker_container)
        self.color_picker_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.color_picker_button.setStyleSheet("""
            QPushButton {
                width: 100px;
                height: 40px;
                border-radius: 8px;
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
        """)

        def open_color_picker():
            color = QColorDialog.getColor()
            if color.isValid():
                rgb_color = (color.red(), color.green(), color.blue())
                self.drawing_canvas.set_color(rgb_color)
                self.color_picker_button.setStyleSheet(f"background-color: {color.name()}; width: 100px; height: 40px; border-radius: 8px;")

        self.color_picker_button.clicked.connect(open_color_picker)
        color_layout.addWidget(self.color_picker_button)


        self.brush_slider = QSlider(Qt.Orientation.Horizontal, self.color_picker_container)
        self.brush_slider.setMinimum(1)
        self.brush_slider.setMaximum(20)
        self.brush_slider.setValue(7)
        self.brush_slider.setFixedWidth(150)
        self.brush_slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.brush_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: white;
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: black;
                width: 20px;
                height: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)
        self.brush_slider.valueChanged.connect(lambda value: self.drawing_canvas.set_brush_thickness(value))
        color_layout.addWidget(self.brush_slider)
        self.reset_canvas_button = QPushButton("Reset Canvas", self.color_picker_container)
        self.reset_canvas_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.reset_canvas_button.setStyleSheet("""
            QPushButton {
                width: 100px;
                height: 40px;
                border-radius: 8px;
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        self.reset_canvas_button.clicked.connect(self.drawing_canvas.clear_canvas)
        color_layout.addWidget(self.reset_canvas_button)


        self.color_picker_container.setLayout(color_layout)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        webcam_x = (screen_geometry.width() - self.webcam_label.width()) + 50
        webcam_y = (screen_geometry.height() - self.webcam_label.height()) - 100
        self.color_picker_container.move(webcam_x, webcam_y - 150)

        self.color_picker_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.color_picker_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.brush_slider.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        self.color_picker_container.show()

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        webcam_x = (screen_geometry.width() - self.webcam_label.width()) + 50  # Align to the right
        webcam_y = (screen_geometry.height() - self.webcam_label.height()) - 100  # Align to the bottom
        self.webcam_label.move(webcam_x, webcam_y)

        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("⚠️ Webcam not accessible!")

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_webcam)
        self.timer.start(30)

        self.button_container.raise_()
        self.emoji_toggle_button.raise_()
        self.sticker_toggle_button.raise_()
        self.upload_button.raise_()
        self.manual_color_button.raise_() 
        self.auto_color_button.raise_()   

        self.lyrics_label.lower()                   
        self.color_picker_container.raise_()        
        self.color_picker_button.raise_()             
        self.brush_slider.raise_()                   
        self.reset_canvas_button.raise_()             
        self.button_container.raise_()                
        self.webcam_label.raise_()                  
        self.bg_label.raise_()                        
        self.drawing_label.raise_()                   
        self.refresh_button.raise_()                  
        self.toggle_button.raise_()                   
        self.sidebar_widget.raise_()                  

        self.lyrics_timer = QTimer()
        self.lyrics_timer.timeout.connect(self.update_real_time_lyrics)
        self.lyrics_timer.start(2000)

        self.emoji_timer = QTimer()
        self.emoji_timer.timeout.connect(self.auto_generate_emoji)
        self.emoji_timer.start(10000)

        self.sticker_timer = QTimer()
        self.sticker_timer.timeout.connect(self.auto_generate_sticker)
        self.sticker_timer.start(15000)


    def resizeEvent(self, event):
            window_width = self.width()
            window_height = self.height()
            x = (window_width - self.bg_label.width()) // 2
            y = (window_height - self.bg_label.height()) // 2
            self.bg_label.move(x, y)


            self.drawing_label.setGeometry(self.bg_label.geometry())

            self.bg_label.raise_()               
            self.drawing_label.raise_()          
            self.refresh_button.raise_()          
            self.toggle_button.raise_()           
            self.manual_color_button.raise_() 
            self.auto_color_button.raise_() 
            self.sidebar_widget.raise_()         
            self.button_container.raise_()        
            self.webcam_label.raise_()           
            self.color_picker_container.raise_()  
            self.lyrics_label.raise_() 
            super().resizeEvent(event)
            

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            print(f"Mouse press at: {event.pos()}")
        return super().eventFilter(obj, event)
        self.installEventFilter(self)
        
    def update_webcam(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.resize(frame, (self.webcam_label.width(), self.webcam_label.height()))
            processed_frame = self.drawing_canvas.process_frame(frame)
            qt_image = QImage(processed_frame.data, processed_frame.shape[1], processed_frame.shape[0], QImage.Format.Format_BGR888)
            self.webcam_label.setPixmap(QPixmap.fromImage(qt_image))
    

    def add_text(self):
        text, ok = QInputDialog.getText(self, 'Add Text', 'Enter your text:')
        if ok and text:
            draggable_text = DraggableText(self, text, 30)  
            draggable_text.show()
            self.set_selected_item(draggable_text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q:
            self.toggle_stickers()  
        super().keyPressEvent(event)

    def toggle_emojis(self):
        self.emoji_enabled = not self.emoji_enabled
        if self.emoji_enabled:
            self.emoji_toggle_button.setText("Emojis: ON")
            self.emoji_toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")
        else:
            self.emoji_toggle_button.setText("Emojis: OFF")
            self.emoji_toggle_button.setStyleSheet("background: white; font-size: 18px; padding: 10px 20px; color: black;")


    def toggle_stickers(self):
        self.sticker_enabled = not self.sticker_enabled
        if self.sticker_enabled:
            self.sticker_toggle_button.setText("AI Stickers: ON")
            print("✅ AI Stickers Enabled (You can disable by pressing Q)")
        else:
            self.sticker_toggle_button.setText("AI Stickers: OFF")
            print("❌ AI Stickers Disabled (You can enable by pressing Q)")

        self.sticker_toggle_button.setStyleSheet(
            "background: white; font-size: 18px; padding: 10px 20px; color: black;"
        )

            

    def auto_generate_sticker(self):
        if not self.sticker_enabled:
            return

        sample_lyrics = self.lyrics_label.text()
        if sample_lyrics and sample_lyrics != "Waiting for lyrics...":
            ai_sticker = DraggableAISticker(self, sample_lyrics)
            ai_sticker.show()
            self.active_stickers.append(ai_sticker)
            self.set_selected_item(ai_sticker)

    def set_selected_item(self, item):
        self.selected_item = item
        self.sidebar_widget.show()

        if isinstance(item, DraggableEmoji):
            self.stacked_layout.setCurrentIndex(0)  
            self.emoji_slider.setValue(item.font().pointSize())
        elif isinstance(item, ResizableDraggableImage):
            self.stacked_layout.setCurrentIndex(1)  
            self.image_slider.setValue(item.width())
        elif isinstance(item, DraggableText):
            self.stacked_layout.setCurrentIndex(0)  
            self.emoji_slider.setValue(item.font().pointSize())
        elif isinstance(item, DraggableAISticker):
            self.stacked_layout.setCurrentIndex(2) 
            self.sticker_slider.setValue(item.width())

    def update_selected_item_size(self):
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
                self.selected_item = None
                self.sidebar_widget.hide()

    def show_full_lyrics(self):
        song_info = get_current_song()
        song_title = song_info[0] if song_info and song_info[0] else "Unknown Song"
        artist_name = song_info[1] if song_info and song_info[1] else "Unknown Artist"

        if self.lyrics_dict:
            full_lyrics = "\n".join(self.lyrics_dict.values())
        else:
            full_lyrics = "Lyrics not found."

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Full Lyrics - {song_title} by {artist_name}")
        dialog.setFixedSize(600, 400)

        title_label = QLabel(f"{song_title} by {artist_name}", dialog)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lyrics_label = QLabel(full_lyrics)
        lyrics_label.setWordWrap(True)
        lyrics_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        lyrics_label.setStyleSheet("font-size: 16px; padding: 10px;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(lyrics_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(300) 
        scroll_area.setStyleSheet("background: transparent; border: none;")


        layout = QVBoxLayout()
        layout.addWidget(title_label)  
        layout.addWidget(scroll_area)
        dialog.setLayout(layout)
        dialog.exec()


    def refresh_lyrics(self):
        self.lyrics_label.setText("Loading...")
        QApplication.processEvents() 
        current_pos = self.lyrics_label.fixed_position
        song_info = get_current_song()

        if not song_info or not song_info[0] or not song_info[1]:
            self.lyrics_label.setText("No song playing or song data unavailable.")
            return

        song, artist = song_info[:2]

        if song == "No song playing" or artist == "Unknown Artist":
            self.lyrics_label.setText("No song playing or song data unavailable.")
            return

        lyrics_result = get_lyrics(song, artist)

        if lyrics_result:
            self.lyrics_dict, _ = lyrics_result
            first_line = next(iter(self.lyrics_dict.values()), "No lyrics available.")
            self.lyrics_label.setText(first_line)
        else:
            self.lyrics_dict = {}
            self.lyrics_label.setText("No lyrics available.")

        self.lyrics_label.move(current_pos)


    def update_real_time_lyrics(self):
        if not self.lyrics_dict:
            return
        current_song = get_current_song()
        if not current_song or current_song[0] == "No song playing":
            return
        current_progress = current_song[2]
        valid_times = {
            t: convert_to_seconds(t)
            for t in self.lyrics_dict
            if convert_to_seconds(t) is not None
        }
        if not valid_times:
            self.lyrics_label.setText("No valid timestamps found.")
            return

        closest_time = min(valid_times, key=lambda t: abs(valid_times[t] - current_progress))
        current_pos = self.lyrics_label.fixed_position 

        self.lyrics_label.setText(self.lyrics_dict[closest_time])
        self.lyrics_label.move(current_pos)


    def auto_generate_emoji(self):
        if not self.emoji_enabled:  
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
            if self.selected_item == old_emoji: 
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
        self.emoji_size = value
        for emoji in self.active_emojis:
            emoji.setFont(QFont(self.custom_font, self.emoji_size))  
            emoji.setFixedSize(self.emoji_size, self.emoji_size)

    def update_image_size(self, value):
        self.image_size = value
        for child in self.children():
            if isinstance(child, ResizableDraggableImage):
                child.resize_image(self.image_size)

    def cleanup_resources(self):
        if self.capture.isOpened():
            self.capture.release()
            print("Webcam resource released.")

    def closeEvent(self, event):
        if self.capture.isOpened():
            self.capture.release()
        
    def remove_background(self, image_path):
        output_path = os.path.join(os.path.dirname(image_path), "removed_bg.png")
        with open(image_path, "rb") as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)
            with open(output_path, "wb") as output_file:
                output_file.write(output_data)
        return output_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_path = "/Users/PearlCxndie_1/Documents/GitHub/SpotifyAPI-Scrapbook/Remingtoned Type.ttf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Failed to load custom font. Falling back to Arial.")
        custom_font = "Arial"
    else:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        print(f"Available font families: {font_families}")
        custom_font = font_families[0] if font_families else "Arial"
        print(f"Custom font loaded: {custom_font}")
    app_font = QFont(custom_font, 12)  
    app.setFont(app_font)
    
    window = LyricsApp()
    window.show()
    sys.exit(app.exec())