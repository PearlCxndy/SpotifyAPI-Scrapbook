import cv2
import numpy as np
import mediapipe as mp
from dorothy import Dorothy
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import QLabel

class HandDrawingCanvas:
    def __init__(self, drawing_label):
    
        self.drawing_label = drawing_label
        self.width = drawing_label.width()
        self.height = drawing_label.height()

        self.color = (255, 0, 0)  # Default drawing color (red)
        self.brush_thickness = 7
        self.prev_x, self.prev_y = None, None
        self.drawing = False

        # Initialize the canvas with a transparent background
        self.canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)  # 4 channels for RGBA
        self.canvas[:, :, 3] = 0  # Set alpha channel to 0 (fully transparent)

        # Reference to the drawing label
        self.drawing_label = drawing_label

        # Initialize Mediapipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def draw_dorothy_brush(self, x, y):
        """Draw using Dorothy's API with smooth and constant strokes."""
        if self.prev_x is not None and self.prev_y is not None:
            cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), self.color + (255,), self.brush_thickness)
        else:
            cv2.circle(self.canvas, (x, y), self.brush_thickness // 2, self.color + (255,), -1)
        self.prev_x, self.prev_y = x, y
        self.update_drawing_label()

    def update_drawing_label(self):
        """Update the drawing label with the current canvas."""
        if isinstance(self.drawing_label, QLabel):
            # Convert the canvas to a QImage with transparency
            qt_image = QImage(self.canvas.data, self.width, self.height, QImage.Format.Format_RGBA8888)
            self.drawing_label.setPixmap(QPixmap.fromImage(qt_image))

    def process_frame(self, frame):
        """Process each frame for hand detection and drawing."""
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, _ = frame.shape
            x, y = int(index_finger_tip.x * self.width), int(index_finger_tip.y * self.height)

            self.draw_dorothy_brush(x, y)
            self.drawing = True
        else:
            self.drawing = False
            self.prev_x, self.prev_y = None, None

        return frame
    def update_canvas_size(self):
        """Update the canvas size based on the drawing_label's size."""
        self.width = self.drawing_label.width()
        self.height = self.drawing_label.height()
        self.canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)  # Ensure 4 channels for transparency
        self.canvas[:, :, 3] = 0  # Keep it fully transparent initially
        self.update_drawing_label()  # Refresh the drawing label

    def clear_canvas(self):
        """Clear Dorothy's canvas."""
        self.canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)  
        self.update_drawing_label()


    def set_color(self, new_color):
        """Set a new drawing color."""
        if isinstance(new_color, QColor):
            self.color = (new_color.red(), new_color.green(), new_color.blue())
        else:
            self.color = new_color

    def set_brush_thickness(self, thickness):
        """Set a new brush thickness."""
        self.brush_thickness = thickness

    def get_canvas(self):
        """Return the current canvas."""
        return self.canvas