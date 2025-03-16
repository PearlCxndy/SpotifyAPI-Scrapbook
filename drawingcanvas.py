import cv2
import numpy as np
import mediapipe as mp
from dorothy import Dorothy
from PyQt6.QtGui import QColor

class HandDrawingCanvas:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.color = (255, 0, 0)
        self.brush_thickness = 7
        self.prev_x, self.prev_y = None, None
        self.drawing = False

        # Initialize Dorothy and manually create the canvas layer
        self.dorothy = Dorothy()
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.dorothy.set_stroke_weight(self.brush_thickness)
        self.dorothy.stroke(self.color)

        # Mediapipe Hand Detection
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils

    def draw_dorothy_brush(self, x, y):
        """Draw using Dorothy's API with smooth and constant strokes."""
        if self.prev_x is not None and self.prev_y is not None:
            self.dorothy.line(pt1=(self.prev_x, self.prev_y), pt2=(x, y), layer=self.canvas)
        else:
            self.dorothy.circle(centre=(x, y), radius=self.brush_thickness // 2, layer=self.canvas)
        self.prev_x, self.prev_y = x, y
        self.dorothy.update_canvas()

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

        # Ensure canvas matches frame size
        dorothy_canvas = cv2.resize(self.canvas, (frame.shape[1], frame.shape[0]))
        output = cv2.addWeighted(frame, 0.7, dorothy_canvas, 0.3, 0)
        return output

    def clear_canvas(self):
        """Clear Dorothy's canvas."""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def set_color(self, new_color):
        """Set a new drawing color."""
        if isinstance(new_color, QColor):
            self.color = (new_color.red(), new_color.green(), new_color.blue())
        else:
            self.color = new_color
        self.dorothy.stroke(self.color)

    def set_brush_thickness(self, thickness):
        """Set a new brush thickness."""
        self.brush_thickness = thickness
        self.dorothy.set_stroke_weight(self.brush_thickness)

    def get_canvas(self):
        """Return the current canvas."""
        return self.canvas
