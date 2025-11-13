import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic

# Load cartoon image
cartoon = cv2.imread("characters/images/1.jpg")
cartoon = cv2.resize(cartoon, (640, 480))

cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    last_head_pos = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = holistic.process(rgb)

        # Get face landmarks for head position
        if result.face_landmarks:
            landmarks = result.face_landmarks.landmark

            # Nose tip as main head position
            nose = landmarks[1]
            left_eye = landmarks[33]
            right_eye = landmarks[263]

            # Compute head movement (x,y)
            h, w, _ = frame.shape
            cx, cy = int(nose.x * w), int(nose.y * h)

            if last_head_pos is not None:
                dx = cx - last_head_pos[0]
                dy = cy - last_head_pos[1]
            else:
                dx, dy = 0, 0

            last_head_pos = (cx, cy)

            # Calculate face rotation (based on eye distance)
            eye_dx = (right_eye.x - left_eye.x)
            rotation = np.degrees(np.arctan2((right_eye.y - left_eye.y), eye_dx))

            # Make a copy of cartoon image to transform
            overlay = cartoon.copy()

            # Translate cartoon based on your head movement
            M = np.float32([[1, 0, dx * 0.5], [0, 1, dy * 0.5]])
            moved = cv2.warpAffine(overlay, M, (overlay.shape[1], overlay.shape[0]))

            # Rotate cartoon slightly according to your head tilt
            center = (overlay.shape[1] // 2, overlay.shape[0] // 2)
            M_rot = cv2.getRotationMatrix2D(center, -rotation, 1)
            rotated = cv2.warpAffine(moved, M_rot, (overlay.shape[1], overlay.shape[0]))

            # Blend cartoon onto a black background
            output = rotated

            # Add text overlay for debugging
            cv2.putText(output, f"Rotation: {rotation:.2f}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            cv2.putText(output, f"Move dx={dx}, dy={dy}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            cv2.imshow("Cartoon Controlled by You", output)
        else:
            cv2.imshow("Cartoon Controlled by You", cartoon)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

cap.release()
cv2.destroyAllWindows()
