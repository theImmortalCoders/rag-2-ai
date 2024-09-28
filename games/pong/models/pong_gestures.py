import cv2
import mediapipe as mp

ruch = 0


def start_gesture_recognition():
    global ruch

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7) as hands:
        previous_y = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Nie można odczytać obrazu z kamery")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    wrist = hand_landmarks.landmark[9]
                    current_y = wrist.y

                    if previous_y is not None:
                        if current_y < previous_y - 0.02:
                            ruch = 1
                        elif current_y > previous_y + 0.02:
                            ruch = -1
                        else:
                            ruch = 0

                    previous_y = current_y

            cv2.imshow('Hand Tracking', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


def get_move_from_gesture():
    return ruch
