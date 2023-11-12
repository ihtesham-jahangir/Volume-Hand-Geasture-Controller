import cv2
import mediapipe as mp
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
# Initialize mediapipe solutions
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Initialize the pycaw volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the volume range
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# Main loop
while True:
    success, image = cap.read()
    if not success:
        continue

    # Convert the BGR image to RGB, flip the image around y-axis for correct handedness output
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # Process the image and draw hand landmarks
    results = hands.process(image)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the hand landmarks
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the coordinates of the thumb tip and index finger tip
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate the distance between thumb tip and index tip
            x1, y1 = thumb_tip.x, thumb_tip.y
            x2, y2 = index_tip.x, index_tip.y
            distance = math.hypot(x2 - x1, y2 - y1)

            # Convert the distance to a volume level
            vol = np.interp(distance, [0.0, 0.2], [minVol, maxVol])  # Adjust the 0.0 and 0.3 values based on your distance range

            # Set the system volume
            volume.SetMasterVolumeLevel(vol, None)

    # Display the image
    cv2.imshow('Volume Control Gesture', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
