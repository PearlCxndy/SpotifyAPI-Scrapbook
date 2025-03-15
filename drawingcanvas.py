import cv2
import numpy as np
import mediapipe as mp
from dorothy import Dorothy

class HandDrawingCanvas:
    def __init__(self, width=600, height=600):
        # Initialize Dorothy
        self.dorothy = Dorothy()
        self.width = width
        self.height = height
        self.canvas = self.dorothy.get_layer()

        # Mediapipe Hand Detection
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils

        # Drawing Attributes
        self.color = self.dorothy.red
        self.drawing = False
        self.prev_x, self.prev_y = None, None
        self.brush_thickness = 7

        # Initialize stroke style
        self.dorothy.stroke(self.color)
        self.dorothy.set_stroke_weight(self.brush_thickness)

    def draw_dorothy_brush(self, x, y):
        """Draw using Dorothy's API with smooth and constant strokes."""
        if self.prev_x is not None and self.prev_y is not None:
            # Draw a continuous line
            self.dorothy.line(
                pt1=(self.prev_x, self.prev_y),
                pt2=(x, y),
                layer=self.canvas
            )
        else:
            # Draw a starting point circle
            self.dorothy.circle(
                centre=(x, y),
                radius=self.brush_thickness // 2,
                layer=self.canvas
            )

        self.prev_x, self.prev_y = x, y

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
            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            self.draw_dorothy_brush(x, y)
            self.drawing = True
        else:
            self.drawing = False
            self.prev_x, self.prev_y = None, None

        # Render the Dorothy layers onto the canvas
        self.dorothy.update_canvas()

        # Convert Dorothy's canvas to OpenCV image and blend it
        dorothy_canvas = self.dorothy.canvas
        if dorothy_canvas.shape != frame.shape:
            dorothy_canvas = cv2.resize(dorothy_canvas, (frame.shape[1], frame.shape[0]))

        output = cv2.addWeighted(frame, 0.3, dorothy_canvas, 0.7, 0)
        return output

    def clear_canvas(self):
        """Clears the Dorothy canvas."""
        self.canvas = self.dorothy.get_layer()
        self.dorothy.update_canvas()

    def set_color(self, new_color):
        """Sets a new drawing color."""
        self.color = new_color
        self.dorothy.stroke(self.color)

    def set_brush_thickness(self, thickness):
        """Sets a new brush thickness."""
        self.brush_thickness = thickness
        self.dorothy.set_stroke_weight(self.brush_thickness)

    def get_canvas(self):
        """Returns the current canvas."""
        return self.dorothy.canvas
