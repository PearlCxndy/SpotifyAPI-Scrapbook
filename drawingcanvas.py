import cv2
import numpy as np
import mediapipe as mp
from dorothy import Dorothy

# Initialize Dorothy for drawing styles
dorothy = Dorothy()

# Initialize Mediapipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Initialize the drawing canvas
canvas = None

# Default drawing color
color = (255, 0, 0)

# Drawing status
drawing = False
prev_x, prev_y = None, None

# Default brush thickness
brush_thickness = 7

# Initialize webcam
cap = cv2.VideoCapture(0)

print("\nInstructions:")
print("- Show 1 finger to draw.")
print("- Click to change color (color wheel).")
print("- Use the resize bar to change brush thickness.")
print("- Grip hand to stop drawing.")
print("- Press 'q' to exit.\n")

def draw_color_wheel(frame):
    """Draws a simple color wheel on the screen."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    for i, c in enumerate(colors):
        cv2.circle(frame, (50, 50 + i * 50), 20, c, -1)
    return colors

def check_color_selection(x, y, colors):
    """Check if the mouse clicked inside any color circle."""
    for i, c in enumerate(colors):
        if 30 < x < 70 and (30 + i * 50) < y < (70 + i * 50):
            return c
    return None

# Mouse callback to change color
def mouse_event(event, x, y, flags, param):
    global color
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_color = check_color_selection(x, y, colors)
        if selected_color:
            color = selected_color
            print(f"Color changed to: {color}")

# Trackbar callback for brush size
def change_brush(val):
    global brush_thickness
    brush_thickness = max(val, 1)  # Avoid zero thickness

cv2.namedWindow("Dorothy Chalk Hand Drawing")
cv2.createTrackbar("Brush Size", "Dorothy Chalk Hand Drawing", brush_thickness, 30, change_brush)
cv2.setMouseCallback("Dorothy Chalk Hand Drawing", mouse_event)

def is_grip(landmarks):
    """Detects if the hand is in a grip (fist) position."""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    distance = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([index_tip.x, index_tip.y]))
    return distance < 0.05

def draw_dorothy_brush(canvas, x, y, color, thickness, prev_x=None, prev_y=None, dorothy=None):
    """Draws with a Dorothy-style textured brush effect using Dorothy's CCI, ensuring connected strokes."""

    def draw_texture_at_point(px, py):
        if dorothy:
            # Use Dorothy's CCI for texture generation
            texture = dorothy.cci(thickness, thickness)
            texture = cv2.resize(texture, (thickness, thickness))
            colored_texture = cv2.addWeighted(texture, 0.8, np.full((thickness, thickness, 3), color, dtype=np.uint8), 0.2, 0)
        else:
            colored_texture = np.full((thickness, thickness, 3), color, dtype=np.uint8)

        y1 = max(int(py - thickness // 2), 0)
        y2 = min(int(py + thickness // 2), canvas.shape[0])
        x1 = max(int(px - thickness // 2), 0)
        x2 = min(int(px + thickness // 2), canvas.shape[1])

        if y1 >= y2 or x1 >= x2:
            return  # Skip drawing if ROI is invalid

        texture_cropped = colored_texture[0:y2 - y1, 0:x2 - x1]
        roi = canvas[y1:y2, x1:x2]

        if roi.shape == texture_cropped.shape:
            blended = cv2.addWeighted(roi, 0.3, texture_cropped, 0.7, 0)
            canvas[y1:y2, x1:x2] = blended

    # Use cv2.line with increased thickness for a continuous and clear stroke
    if prev_x is not None and prev_y is not None:
        cv2.line(canvas, (prev_x, prev_y), (x, y), color, thickness + 2)
        dist = int(np.hypot(x - prev_x, y - prev_y))
        for i in np.linspace(0, 1, dist * 5):  # Increase density for smoother lines
            interp_x = int(prev_x + (x - prev_x) * i)
            interp_y = int(prev_y + (y - prev_y) * i)
            draw_texture_at_point(interp_x, interp_y)
    else:
        draw_texture_at_point(x, y)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    if canvas is None:
        canvas = np.zeros_like(frame)

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect hands (only one hand allowed for better performance)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if is_grip(hand_landmarks.landmark):
            drawing = False
            prev_x, prev_y = None, None
        else:
            # Extract index finger tip coordinates
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, _ = frame.shape
            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            if drawing and prev_x is not None and prev_y is not None:
                draw_dorothy_brush(canvas, x, y, color, brush_thickness)

            drawing = True
            prev_x, prev_y = x, y

    else:
        drawing = False
        prev_x, prev_y = None, None

    # Draw color wheel and combine frame with canvas
    colors = draw_color_wheel(frame)
    output = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    cv2.imshow("Dorothy Chalk Hand Drawing", output)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()