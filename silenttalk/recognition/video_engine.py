"""
Video Sign Language Recognition Engine
Processes uploaded video files frame-by-frame using a dedicated MediaPipe instance.
Extracts sign language letters with confidence scores and assembles them into text.

Strategy:
  - Capture one frame every 1 second (configurable)
  - At this rate, each frame represents a deliberate sign — no jitter to filter
  - Register a sign immediately if confidence > threshold
  - 2-second cooldown prevents the same letter from being registered twice
    when the signer holds a sign across multiple captures
  - Different letters register instantly (no cooldown between different signs)
"""
import cv2
import mediapipe as mp
import numpy as np
import os
import time
import pickle

# ── Load the same model used by ai_engine ────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.p")
model_dict = pickle.load(open(MODEL_PATH, "rb"))
_model = model_dict["model"]

LABELS_DICT = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
    10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
    19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z',
    26: '0', 27: '1', 28: '2', 29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9',
    36: ' ', 37: '.'
}

EXPECTED_FEATURES = 42  # 21 landmarks × 2 coordinates (x, y)


def _predict_frame_standalone(hands_instance, frame_rgb):
    """
    Predict sign from a single RGB frame using a DEDICATED MediaPipe Hands instance.
    Returns (letter, confidence) tuple, or (None, 0.0) if no hand detected.
    """
    data_aux = []
    x_ = []
    y_ = []

    results = hands_instance.process(frame_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        for lm in hand_landmarks.landmark:
            x_.append(lm.x)
            y_.append(lm.y)

        min_x, min_y = min(x_), min(y_)
        for lm in hand_landmarks.landmark:
            data_aux.append(lm.x - min_x)
            data_aux.append(lm.y - min_y)

        # Pad or truncate
        if len(data_aux) < EXPECTED_FEATURES:
            data_aux.extend([0] * (EXPECTED_FEATURES - len(data_aux)))
        elif len(data_aux) > EXPECTED_FEATURES:
            data_aux = data_aux[:EXPECTED_FEATURES]

        features = np.asarray(data_aux).reshape(1, -1)
        prediction = _model.predict(features)

        # Get confidence from predict_proba
        confidence = 0.0
        if hasattr(_model, 'predict_proba'):
            proba = _model.predict_proba(features)[0]
            confidence = round(float(max(proba)) * 100, 1)

        letter = LABELS_DICT.get(int(prediction[0]), "?")
        return letter, confidence

    return None, 0.0


def process_video_file(video_path, capture_every_sec=1.0, min_confidence=30.0, same_letter_cooldown_sec=2.0):
    """
    Process a video file and extract sign language text.

    Args:
        video_path:               Path to the video file
        capture_every_sec:        Sample one frame every N seconds (default: 1.0)
        min_confidence:           Minimum model confidence % to register a sign (default: 30)
        same_letter_cooldown_sec: Seconds to wait before allowing the SAME letter again (default: 2.0)
                                  Different letters always register immediately.

    Returns dict with: text, timeline (with timestamps + confidence), stats
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"text": "", "timeline": [], "stats": {"error": "Could not open video file"}}

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    # How many frames to skip between captures
    frame_skip = max(1, int(fps * capture_every_sec))
    cooldown_frames = int(fps * same_letter_cooldown_sec)

    # Create a DEDICATED hands instance for video processing (static mode!)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        min_detection_confidence=0.5,
        max_num_hands=1
    )

    # Processing state
    sentence = ""
    timeline = []
    last_registered_letter = ""
    last_registered_frame = -999

    frame_idx = 0
    processed_count = 0
    detected_count = 0

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Only process one frame every capture_every_sec seconds
        if frame_idx % frame_skip != 0:
            frame_idx += 1
            continue

        processed_count += 1
        timestamp = round(frame_idx / fps, 2)

        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run prediction
        letter, confidence = _predict_frame_standalone(hands, frame_rgb)

        if letter and confidence >= min_confidence:
            detected_count += 1

            # Cooldown logic:
            #   - DIFFERENT letter → always register immediately
            #   - SAME letter → only register if cooldown has passed
            is_different_letter = (letter != last_registered_letter)
            cooldown_passed = (frame_idx - last_registered_frame) > cooldown_frames

            if is_different_letter or cooldown_passed:
                sentence += letter
                timeline.append({
                    "time": timestamp,
                    "letter": letter,
                    "frame": frame_idx,
                    "confidence": confidence,
                    "method": "hand_landmarks",
                })
                last_registered_letter = letter
                last_registered_frame = frame_idx

        elif not letter:
            # No hand detected — reset the "last letter" so the next
            # detection of any letter registers immediately
            last_registered_letter = ""

        frame_idx += 1

    cap.release()
    hands.close()
    processing_time = round(time.time() - start_time, 2)

    return {
        "text": sentence,
        "timeline": timeline,
        "stats": {
            "total_frames": total_frames,
            "processed_frames": processed_count,
            "detected_frames": detected_count,
            "duration_seconds": round(duration, 2),
            "processing_time_seconds": processing_time,
            "fps": round(fps, 1),
            "letters_found": len(timeline),
            "capture_interval": f"{capture_every_sec}s",
            "min_confidence": f"{min_confidence}%",
        }
    }
