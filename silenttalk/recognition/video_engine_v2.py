"""
Video Sign Language Recognition Engine v2 — Multi-Tier Architecture
===================================================================

Replaces the naive letter-by-letter approach with a proper pipeline:

  Stage 1  →  MediaPipe Holistic (1662 features/frame, not just 42)
  Stage 2  →  Motion-energy activity segmentation
  Stage 3  →  Multi-tier classification:
                Tier 1: LSTM word recognition  (action.h5 — hello/thanks/iloveyou)
                Tier 2: RandomForest letters   (model.p — A-Z, 0-9, space, .)
                Tier 3: MediaPipe gestures     (7 pre-trained gestures)
  Stage 4  →  Temporal smoothing + smart text assembly

Author: SilentTalk AI Engine v2
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import time
import pickle
import traceback

# ── Processing Limits ─────────────────────────────────────────────
# Resize large frames (4K etc.) to this max dimension before processing.
# MediaPipe works best with 480-720p frames; larger wastes memory and CPU.
MAX_PROCESSING_DIMENSION = 720
# Cap total processed frames to avoid OOM on very long videos
MAX_PROCESSED_FRAMES = 500

# ═══════════════════════════════════════════════════════════════════
# MODEL LOADING
# ═══════════════════════════════════════════════════════════════════

# ── Tier 1: LSTM Word-Level Model ────────────────────────────────
_lstm_model = None
LSTM_ACTIONS = np.array(['hello', 'thanks', 'iloveyou'])
LSTM_SEQUENCE_LENGTH = 30
LSTM_THRESHOLD = 0.6  # Minimum confidence for LSTM prediction

def _load_lstm_model():
    """Lazy-load the LSTM model to avoid slowing down server startup."""
    global _lstm_model
    if _lstm_model is not None:
        return _lstm_model

    try:
        # Try multiple possible locations for action.h5
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "action.h5"),
            os.path.join(os.path.dirname(__file__), "..", "..", "ActionDetectionforSignLanguage", "action.h5"),
        ]
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                from tensorflow.keras.models import load_model
                _lstm_model = load_model(abs_path)
                print(f"[VideoEngineV2] LSTM model loaded from: {abs_path}")
                print(f"[VideoEngineV2]   Input shape:  {_lstm_model.input_shape}")
                print(f"[VideoEngineV2]   Output shape: {_lstm_model.output_shape}")
                print(f"[VideoEngineV2]   Actions: {LSTM_ACTIONS.tolist()}")
                return _lstm_model

        print("[VideoEngineV2] WARNING: action.h5 not found — LSTM tier disabled")
        return None
    except Exception as e:
        print(f"[VideoEngineV2] ERROR loading LSTM model: {e}")
        return None


# ── Tier 2: RandomForest Letter Model ────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.p")
_rf_model = None
if os.path.exists(MODEL_PATH):
    model_dict = pickle.load(open(MODEL_PATH, "rb"))
    _rf_model = model_dict["model"]
    print(f"[VideoEngineV2] RandomForest model loaded from: {MODEL_PATH}")

LABELS_DICT = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
    10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
    19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z',
    26: '0', 27: '1', 28: '2', 29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9',
    36: ' ', 37: '.'
}
RF_EXPECTED_FEATURES = 42  # 21 landmarks × 2 (x, y)


# ── Tier 3: Gesture Recognizer (lazy-loaded) ─────────────────────
_gesture_recognizer = None

def _load_gesture_recognizer():
    """Lazy-load MediaPipe gesture recognizer."""
    global _gesture_recognizer
    if _gesture_recognizer is not None:
        return _gesture_recognizer
    try:
        from .gesture_engine import recognize_gesture
        _gesture_recognizer = recognize_gesture
        print("[VideoEngineV2] Gesture recognizer loaded")
        return _gesture_recognizer
    except Exception as e:
        print(f"[VideoEngineV2] WARNING: Gesture engine unavailable: {e}")
        return None


# Gesture display name mapping
GESTURE_DISPLAY = {
    "Closed_Fist": "Fist ✊",
    "Open_Palm": "Open Palm 🖐️",
    "Pointing_Up": "Point Up ☝️",
    "Thumb_Down": "Thumbs Down 👎",
    "Thumb_Up": "Thumbs Up 👍",
    "Victory": "Victory ✌️",
    "ILoveYou": "I Love You 🤟",
}


class HolisticMimic:
    """A helper class to wrap/mimic MediaPipe Holistic results.
    Allows us to populate hand landmarks from the fallback Hands model when Holistic fails."""
    def __init__(self, pose_landmarks=None, face_landmarks=None, left_hand_landmarks=None, right_hand_landmarks=None):
        self.pose_landmarks = pose_landmarks
        self.face_landmarks = face_landmarks
        self.left_hand_landmarks = left_hand_landmarks
        self.right_hand_landmarks = right_hand_landmarks


# ═══════════════════════════════════════════════════════════════════
# STAGE 1: HOLISTIC POSE EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def _extract_keypoints_holistic(results):
    """
    Extract 1662 keypoint features from a MediaPipe Holistic result.

    This is the SAME format used by action.h5 (from ActionDetectionforSignLanguage):
      - Pose:       33 landmarks × 4 (x, y, z, visibility) = 132
      - Face:      468 landmarks × 3 (x, y, z)             = 1404
      - Left Hand:  21 landmarks × 3 (x, y, z)             = 63
      - Right Hand: 21 landmarks × 3 (x, y, z)             = 63
      - Total:                                              = 1662
    """
    pose = (
        np.array([[res.x, res.y, res.z, res.visibility]
                  for res in results.pose_landmarks.landmark]).flatten()
        if results.pose_landmarks
        else np.zeros(33 * 4)
    )
    face = (
        np.array([[res.x, res.y, res.z]
                  for res in results.face_landmarks.landmark]).flatten()
        if results.face_landmarks
        else np.zeros(468 * 3)
    )
    lh = (
        np.array([[res.x, res.y, res.z]
                  for res in results.left_hand_landmarks.landmark]).flatten()
        if results.left_hand_landmarks
        else np.zeros(21 * 3)
    )
    rh = (
        np.array([[res.x, res.y, res.z]
                  for res in results.right_hand_landmarks.landmark]).flatten()
        if results.right_hand_landmarks
        else np.zeros(21 * 3)
    )
    return np.concatenate([pose, face, lh, rh])


def _extract_hand_features(results):
    """
    Extract 42 hand-only features for the RandomForest model.
    Uses the first detected hand from Holistic results.
    Returns (features, confidence) or (None, 0.0).
    """
    # Try right hand first (more common for signing), then left hand
    hand_landmarks = None
    if results.right_hand_landmarks:
        hand_landmarks = results.right_hand_landmarks
    elif results.left_hand_landmarks:
        hand_landmarks = results.left_hand_landmarks

    if hand_landmarks is None:
        return None, 0.0

    data_aux = []
    x_ = []
    y_ = []

    for lm in hand_landmarks.landmark:
        x_.append(lm.x)
        y_.append(lm.y)

    min_x, min_y = min(x_), min(y_)
    for lm in hand_landmarks.landmark:
        data_aux.append(lm.x - min_x)
        data_aux.append(lm.y - min_y)

    # Pad or truncate to expected size
    if len(data_aux) < RF_EXPECTED_FEATURES:
        data_aux.extend([0] * (RF_EXPECTED_FEATURES - len(data_aux)))
    elif len(data_aux) > RF_EXPECTED_FEATURES:
        data_aux = data_aux[:RF_EXPECTED_FEATURES]

    return np.asarray(data_aux), 1.0  # confidence = hand detection quality


def _has_hand(results):
    """Check if any hand was detected in this frame's Holistic results."""
    return (results.left_hand_landmarks is not None or
            results.right_hand_landmarks is not None)


# ═══════════════════════════════════════════════════════════════════
# STAGE 2: MOTION-ENERGY ACTIVITY SEGMENTATION
# ═══════════════════════════════════════════════════════════════════

def _compute_motion_energy(keypoints_sequence):
    """
    Compute per-frame motion energy from the keypoint sequence.
    Motion energy = sum of Euclidean distances between consecutive frames'
    hand + pose keypoints (ignoring face to reduce noise).

    Returns array of motion energy values (length = len(sequence) - 1).
    """
    if len(keypoints_sequence) < 2:
        return np.array([0.0])

    energies = []
    for i in range(1, len(keypoints_sequence)):
        prev = keypoints_sequence[i - 1]
        curr = keypoints_sequence[i]

        # Focus on pose (0:132) + left hand (1536:1599) + right hand (1599:1662)
        # Skip face (132:1536) to reduce noise from facial micro-movements
        prev_motion = np.concatenate([prev[0:132], prev[1536:1662]])
        curr_motion = np.concatenate([curr[0:132], curr[1536:1662]])

        energy = np.sqrt(np.sum((curr_motion - prev_motion) ** 2))
        energies.append(energy)

    return np.array(energies)


def _segment_activity(keypoints_sequence, hand_detected_flags, fps,
                      min_segment_frames=8, max_segment_frames=90,
                      merge_gap_frames=5):
    """
    Segment the video into active signing regions based on:
    1. Hand detection (primary signal)
    2. Motion energy (secondary — to split held poses from transitions)

    Returns list of dicts: [{start_frame, end_frame, has_motion}, ...]
    """
    n = len(keypoints_sequence)
    if n == 0:
        return []

    # Step 1: Find contiguous regions where a hand is detected
    segments = []
    in_segment = False
    seg_start = 0

    for i in range(n):
        if hand_detected_flags[i] and not in_segment:
            seg_start = i
            in_segment = True
        elif not hand_detected_flags[i] and in_segment:
            segments.append({"start_frame": seg_start, "end_frame": i - 1})
            in_segment = False

    if in_segment:
        segments.append({"start_frame": seg_start, "end_frame": n - 1})

    # Step 2: Merge segments that are very close together (gap < merge_gap)
    merged = []
    for seg in segments:
        if merged and (seg["start_frame"] - merged[-1]["end_frame"]) <= merge_gap_frames:
            merged[-1]["end_frame"] = seg["end_frame"]
        else:
            merged.append(dict(seg))

    # Step 3: Filter out very short segments (noise) and split very long ones
    final = []
    for seg in merged:
        seg_len = seg["end_frame"] - seg["start_frame"] + 1
        if seg_len < min_segment_frames:
            continue  # Too short — likely noise

        if seg_len > max_segment_frames:
            # Split long segments using motion energy valleys
            energies = _compute_motion_energy(
                keypoints_sequence[seg["start_frame"]:seg["end_frame"] + 1]
            )
            # Find low-energy points (transitions between signs)
            if len(energies) > 10:
                threshold = np.percentile(energies, 25)
                split_points = []
                # Look for sustained low-energy regions
                window = max(3, int(fps * 0.2))
                for j in range(window, len(energies) - window):
                    local_energy = np.mean(energies[max(0, j - window):j + window])
                    if local_energy < threshold:
                        split_points.append(j + seg["start_frame"])

                # Use split points to create sub-segments
                if split_points:
                    prev_start = seg["start_frame"]
                    for sp in split_points[::int(fps * 0.5)]:  # Don't split too often
                        if sp - prev_start >= min_segment_frames:
                            final.append({"start_frame": prev_start, "end_frame": sp})
                            prev_start = sp + 1
                    if seg["end_frame"] - prev_start >= min_segment_frames:
                        final.append({"start_frame": prev_start, "end_frame": seg["end_frame"]})
                    continue

        final.append(seg)

    return final


# ═══════════════════════════════════════════════════════════════════
# STAGE 3: MULTI-TIER CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════

def _resample_sequence(sequence, target_length):
    """
    Resample a variable-length keypoint sequence to a fixed target_length.
    Uses linear interpolation to handle any input length.
    """
    n = len(sequence)
    if n == 0:
        return np.zeros((target_length, sequence.shape[1] if len(sequence.shape) > 1 else 1662))
    if n == target_length:
        return np.array(sequence)

    indices = np.linspace(0, n - 1, target_length)
    resampled = []
    for idx in indices:
        lower = int(np.floor(idx))
        upper = min(lower + 1, n - 1)
        frac = idx - lower
        interpolated = sequence[lower] * (1 - frac) + sequence[upper] * frac
        resampled.append(interpolated)

    return np.array(resampled)


def _classify_segment_lstm(keypoints_segment):
    """
    Tier 1: LSTM Word-Level Classification.
    Takes a segment of holistic keypoints, resamples to 30 frames,
    and predicts using the action.h5 model.

    Returns (word, confidence, 'lstm') or (None, 0.0, 'lstm').
    """
    model = _load_lstm_model()
    if model is None:
        return None, 0.0, "lstm"

    try:
        # Resample to 30 frames as expected by the LSTM
        resampled = _resample_sequence(
            np.array(keypoints_segment), LSTM_SEQUENCE_LENGTH
        )

        # Predict
        prediction = model.predict(np.expand_dims(resampled, axis=0), verbose=0)[0]
        confidence = float(np.max(prediction))
        predicted_idx = int(np.argmax(prediction))

        if confidence >= LSTM_THRESHOLD and predicted_idx < len(LSTM_ACTIONS):
            word = LSTM_ACTIONS[predicted_idx]
            return word, round(confidence * 100, 1), "lstm"

        return None, round(confidence * 100, 1), "lstm"

    except Exception as e:
        print(f"[VideoEngineV2] LSTM prediction error: {e}")
        return None, 0.0, "lstm"


def _classify_segment_rf(keypoints_segment, holistic_results_segment):
    """
    Tier 2: RandomForest Fingerspelling Classification.
    Runs the RF model on multiple frames within the segment and
    uses confidence-weighted majority voting.

    Returns (letter, confidence, 'fingerspelling') or (None, 0.0, 'fingerspelling').
    """
    if _rf_model is None:
        return None, 0.0, "fingerspelling"

    try:
        # Sample up to 5 evenly-spaced frames from the segment
        n = len(holistic_results_segment)
        sample_indices = np.linspace(0, n - 1, min(5, n), dtype=int)

        votes = {}  # letter → list of confidence scores

        for idx in sample_indices:
            results = holistic_results_segment[idx]
            features, _ = _extract_hand_features(results)

            if features is not None:
                feat_array = features.reshape(1, -1)
                prediction = _rf_model.predict(feat_array)
                letter = LABELS_DICT.get(int(prediction[0]), "?")

                # Get confidence via predict_proba
                conf = 0.0
                if hasattr(_rf_model, 'predict_proba'):
                    proba = _rf_model.predict_proba(feat_array)[0]
                    conf = float(max(proba)) * 100

                if letter not in votes:
                    votes[letter] = []
                votes[letter].append(conf)

        if not votes:
            return None, 0.0, "fingerspelling"

        # Weighted majority vote: pick the letter with highest average confidence
        best_letter = None
        best_score = 0.0
        for letter, confidences in votes.items():
            avg_conf = np.mean(confidences)
            vote_weight = len(confidences) / len(sample_indices)  # fraction of frames
            score = avg_conf * vote_weight
            if score > best_score:
                best_score = score
                best_letter = letter

        if best_letter and best_score >= 25.0:  # Minimum viable confidence
            return best_letter, round(best_score, 1), "fingerspelling"

        return None, 0.0, "fingerspelling"

    except Exception as e:
        print(f"[VideoEngineV2] RF prediction error: {e}")
        return None, 0.0, "fingerspelling"


def _classify_segment_gesture(holistic_results_segment, frames_rgb_segment):
    """
    Tier 3: MediaPipe Gesture Recognition.
    Runs the gesture recognizer on the best frame (middle of segment).

    Returns (gesture_display, confidence, 'gesture') or (None, 0.0, 'gesture').
    """
    recognizer = _load_gesture_recognizer()
    if recognizer is None:
        return None, 0.0, "gesture"

    try:
        # Use middle frame of the segment
        mid_idx = len(frames_rgb_segment) // 2
        sample_indices = [mid_idx]

        # Also try quarter and three-quarter frames for robustness
        if len(frames_rgb_segment) > 4:
            sample_indices = [
                len(frames_rgb_segment) // 4,
                mid_idx,
                3 * len(frames_rgb_segment) // 4
            ]

        best_gesture = None
        best_confidence = 0.0
        best_display = None

        for idx in sample_indices:
            frame_rgb = frames_rgb_segment[idx]
            name, display, confidence = recognizer(frame_rgb)
            if name and name != "None" and confidence > best_confidence:
                best_gesture = name
                best_display = display or GESTURE_DISPLAY.get(name, name)
                best_confidence = confidence

        if best_gesture and best_confidence >= 0.5:
            return best_display, round(best_confidence * 100, 1), "gesture"

        return None, 0.0, "gesture"

    except Exception as e:
        print(f"[VideoEngineV2] Gesture prediction error: {e}")
        return None, 0.0, "gesture"


def _fuse_predictions(lstm_result, rf_result, gesture_result):
    """
    Fusion logic: pick the best prediction across tiers.

    Priority (for tie-breaking): LSTM Word > Gesture > Fingerspelling
    This is because word-level and gesture recognition are more meaningful
    than individual letters in real sign language communication.
    """
    results = []

    text, conf, method = lstm_result
    if text is not None:
        results.append({"text": text, "confidence": conf, "method": method, "priority": 3})

    text, conf, method = gesture_result
    if text is not None:
        results.append({"text": text, "confidence": conf, "method": method, "priority": 2})

    text, conf, method = rf_result
    if text is not None:
        results.append({"text": text, "confidence": conf, "method": method, "priority": 1})

    if not results:
        return None, 0.0, "none"

    # Sort by confidence first, then priority for tie-breaking
    results.sort(key=lambda r: (r["confidence"], r["priority"]), reverse=True)
    best = results[0]
    return best["text"], best["confidence"], best["method"]


# ═══════════════════════════════════════════════════════════════════
# STAGE 4: POST-PROCESSING & TEXT ASSEMBLY
# ═══════════════════════════════════════════════════════════════════

def _assemble_text(detections):
    """
    Assemble a sequence of detected signs into readable text.

    Rules:
    - Words (from LSTM/Gesture) are separated by spaces
    - Consecutive letters (from fingerspelling) are grouped together
    - Duplicate adjacent words from held signs are collapsed
    - First letter is capitalized
    """
    if not detections:
        return ""

    parts = []
    prev_text = None
    prev_method = None
    letter_buffer = ""

    for det in detections:
        text = det["text"]
        method = det["method"]

        # Skip duplicates (same text detected in consecutive segments)
        if text == prev_text and method == prev_method:
            continue

        if method == "fingerspelling":
            # Accumulate letters
            letter_buffer += text
        else:
            # Flush letter buffer if we have one
            if letter_buffer:
                parts.append(letter_buffer)
                letter_buffer = ""
            # Add word/gesture
            parts.append(text)

        prev_text = text
        prev_method = method

    # Flush remaining letters
    if letter_buffer:
        parts.append(letter_buffer)

    # Join with spaces and clean up
    sentence = " ".join(parts).strip()

    # Capitalize first letter
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]

    return sentence


def _detect_emotion_from_landmarks(face_landmarks):
    """
    Detect emotion from face landmarks geometry.
    Simplified version of ai_engine.detect_emotion using raw landmarks.
    Returns one of: 'happy', 'sad', 'urgent', 'surprised', 'neutral'
    """
    if face_landmarks is None:
        return "neutral"

    landmarks = face_landmarks.landmark

    # Key landmark indices (same as ai_engine.py)
    mouth_left   = landmarks[61]
    mouth_right  = landmarks[291]
    mouth_top    = landmarks[13]
    mouth_bottom = landmarks[14]
    brow_left    = landmarks[70]
    brow_right   = landmarks[300]
    eye_top      = landmarks[159]
    eye_bottom   = landmarks[145]

    mouth_open = abs(mouth_top.y - mouth_bottom.y)
    mouth_center_y = (mouth_top.y + mouth_bottom.y) / 2
    corners_avg_y = (mouth_left.y + mouth_right.y) / 2
    smile_score = mouth_center_y - corners_avg_y
    brow_avg_y = (brow_left.y + brow_right.y) / 2
    eye_avg_y = (eye_top.y + eye_bottom.y) / 2
    brow_raise = eye_avg_y - brow_avg_y
    eye_open = abs(eye_top.y - eye_bottom.y)

    if smile_score > 0.01 and mouth_open < 0.04:
        return "happy"
    elif brow_raise > 0.08 and eye_open > 0.025:
        return "urgent"
    elif smile_score < -0.005:
        return "sad"
    elif mouth_open > 0.06:
        return "surprised"
    else:
        return "neutral"


# ═══════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════

def process_video_v2(video_path, frame_sample_rate=2, min_confidence=25.0):
    """
    Process a video file using the multi-tier architecture.

    Args:
        video_path:        Path to the video file
        frame_sample_rate: Process every Nth frame (default: 2 = every other frame)
                           Lower = more accurate but slower
        min_confidence:    Minimum confidence % for final output (default: 25)

    Returns dict with:
        text:             Assembled sentence
        timeline:         Per-segment detection details
        stats:            Processing statistics
        emotion_summary:  Dominant emotion detected
    """
    start_time = time.time()

    # ── Open video ────────────────────────────────────────────────
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "text": "",
            "timeline": [],
            "stats": {"error": "Could not open video file"},
            "emotion_summary": "neutral"
        }

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Auto-increase sample rate for very high-res or very long videos
    estimated_sampled = total_frames // frame_sample_rate
    if estimated_sampled > MAX_PROCESSED_FRAMES:
        frame_sample_rate = max(frame_sample_rate, total_frames // MAX_PROCESSED_FRAMES)
        print(f"[VideoEngineV2] Auto-adjusted sample rate to {frame_sample_rate} (too many frames)")

    print(f"[VideoEngineV2] Processing: {total_frames} frames, {frame_w}x{frame_h}, {fps:.1f} FPS, {duration:.1f}s duration")

    # ── STAGE 1: Extract holistic keypoints from every Nth frame ──
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(
        static_image_mode=True,       # True for video file processing (no tracking)
        model_complexity=1,           # 0=lite, 1=full, 2=heavy
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # Fallback Hands model for close-up hand videos where Holistic fails (e.g. no face/body visible)
    mp_hands = mp.solutions.hands
    hands_fallback = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
    )

    all_keypoints = []         # 1662-dim vectors for LSTM
    all_holistic_results = []  # Mimic results containing hands data
    all_frames_rgb = []        # RGB frames for gesture recognizer
    hand_detected = []         # Boolean per frame
    face_landmarks_list = []   # Face landmarks for emotion
    frame_indices = []         # Original frame index for timestamp calculation

    frame_idx = 0
    processed_count = 0
    fallback_count = 0

    print(f"[VideoEngineV2] Stage 1: Extracting keypoints (every {frame_sample_rate} frames)...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_sample_rate != 0:
            frame_idx += 1
            continue

        # Stop if we've hit the frame limit (prevents OOM on very long videos)
        if processed_count >= MAX_PROCESSED_FRAMES:
            print(f"[VideoEngineV2] Hit frame limit ({MAX_PROCESSED_FRAMES}), stopping extraction")
            break

        processed_count += 1

        # ── Resize large frames (e.g. 4K) to save memory & speed up MediaPipe ──
        h, w = frame.shape[:2]
        if max(h, w) > MAX_PROCESSING_DIMENSION:
            scale = MAX_PROCESSING_DIMENSION / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            results = holistic.process(frame_rgb)
        except Exception as e:
            print(f"[VideoEngineV2] Holistic error on frame {frame_idx}: {e}")
            frame_idx += 1
            processed_count -= 1  # Don't count failed frames
            continue

        # Wrap results in a mutable mimic structure
        mimic = HolisticMimic(
            pose_landmarks=results.pose_landmarks,
            face_landmarks=results.face_landmarks,
            left_hand_landmarks=results.left_hand_landmarks,
            right_hand_landmarks=results.right_hand_landmarks
        )

        # Fallback to Hands if Holistic couldn't detect any hands
        if not (mimic.left_hand_landmarks or mimic.right_hand_landmarks):
            try:
                hands_results = hands_fallback.process(frame_rgb)
                if hands_results.multi_hand_landmarks:
                    fallback_count += 1
                    for hand_idx, hand_landmarks in enumerate(hands_results.multi_hand_landmarks):
                        handedness = hands_results.multi_handedness[hand_idx].classification[0].label
                        if handedness == "Left":
                            mimic.left_hand_landmarks = hand_landmarks
                        else:
                            mimic.right_hand_landmarks = hand_landmarks
            except Exception as e:
                print(f"[VideoEngineV2] Hands fallback error on frame {frame_idx}: {e}")

        # Extract 1662 holistic keypoints from mimic
        keypoints = _extract_keypoints_holistic(mimic)
        all_keypoints.append(keypoints)
        all_holistic_results.append(mimic)
        all_frames_rgb.append(frame_rgb)  # Now stores resized frames (not 4K originals)
        hand_detected.append(_has_hand(mimic))
        frame_indices.append(frame_idx)

        # Track face landmarks for emotion
        face_landmarks_list.append(
            mimic.face_landmarks if mimic.face_landmarks else None
        )

        frame_idx += 1

    cap.release()
    holistic.close()
    hands_fallback.close()

    stage1_time = time.time() - start_time
    print(f"[VideoEngineV2] Stage 1 complete: {processed_count} frames processed in {stage1_time:.1f}s (Used Hands fallback on {fallback_count} frames)")

    if processed_count == 0:
        return {
            "text": "",
            "timeline": [],
            "stats": {"error": "No frames could be read from video"},
            "emotion_summary": "neutral"
        }

    # ── STAGE 2: Segment active signing regions ───────────────────
    stage2_start = time.time()
    effective_fps = fps / frame_sample_rate
    segments = _segment_activity(
        all_keypoints, hand_detected, effective_fps,
        min_segment_frames=max(3, int(effective_fps * 0.3)),  # Min ~0.3s
        max_segment_frames=int(effective_fps * 3.0),          # Max ~3.0s per segment
        merge_gap_frames=max(2, int(effective_fps * 0.3)),    # Merge gaps < 0.3s
    )
    stage2_time = time.time() - stage2_start
    print(f"[VideoEngineV2] Stage 2 complete: {len(segments)} segments found in {stage2_time:.2f}s")

    # If no segments found via hand detection, fall back to processing the whole video
    if not segments and any(hand_detected):
        segments = [{"start_frame": 0, "end_frame": len(all_keypoints) - 1}]
        print("[VideoEngineV2] Fallback: treating entire video as one segment")

    # ── STAGE 3: Multi-tier classification per segment ────────────
    stage3_start = time.time()
    detections = []
    tier_counts = {"lstm": 0, "fingerspelling": 0, "gesture": 0}

    for seg_idx, seg in enumerate(segments):
        sf = seg["start_frame"]
        ef = seg["end_frame"]
        seg_keypoints = all_keypoints[sf:ef + 1]
        seg_results = all_holistic_results[sf:ef + 1]
        seg_frames = all_frames_rgb[sf:ef + 1]

        # Calculate timestamp from original frame index
        orig_frame = frame_indices[sf] if sf < len(frame_indices) else 0
        timestamp = round(orig_frame / fps, 2)

        # Run all three tiers (each wrapped in try/except for isolation)
        try:
            lstm_result = _classify_segment_lstm(seg_keypoints)
        except Exception as e:
            print(f"[VideoEngineV2] LSTM error on segment {seg_idx}: {e}")
            lstm_result = (None, 0.0, "lstm")

        try:
            rf_result = _classify_segment_rf(seg_keypoints, seg_results)
        except Exception as e:
            print(f"[VideoEngineV2] RF error on segment {seg_idx}: {e}")
            rf_result = (None, 0.0, "fingerspelling")

        try:
            gesture_result = _classify_segment_gesture(seg_results, seg_frames)
        except Exception as e:
            print(f"[VideoEngineV2] Gesture error on segment {seg_idx}: {e}")
            gesture_result = (None, 0.0, "gesture")

        # Fuse results
        text, confidence, method = _fuse_predictions(lstm_result, rf_result, gesture_result)

        if text and confidence >= min_confidence:
            tier_counts[method] = tier_counts.get(method, 0) + 1

            # Get emotion for this segment
            mid_face = face_landmarks_list[min((sf + ef) // 2, len(face_landmarks_list) - 1)]
            emotion = _detect_emotion_from_landmarks(mid_face)

            detections.append({
                "text": text,
                "confidence": confidence,
                "method": method,
                "time": timestamp,
                "frame": orig_frame,
                "segment_idx": seg_idx,
                "segment_frames": ef - sf + 1,
                "emotion": emotion,
                # Include all tier results for transparency
                "tiers": {
                    "lstm": {"text": lstm_result[0], "confidence": lstm_result[1]},
                    "fingerspelling": {"text": rf_result[0], "confidence": rf_result[1]},
                    "gesture": {"text": gesture_result[0], "confidence": gesture_result[1]},
                }
            })

    stage3_time = time.time() - stage3_start
    print(f"[VideoEngineV2] Stage 3 complete: {len(detections)} detections in {stage3_time:.1f}s")

    # ── STAGE 4: Assemble text + Analytics ────────────────────────
    sentence = _assemble_text(detections)

    # Determine dominant emotion
    emotions = [d.get("emotion", "neutral") for d in detections]
    if emotions:
        from collections import Counter
        emotion_counts = Counter(emotions)
        dominant_emotion = emotion_counts.most_common(1)[0][0]
    else:
        dominant_emotion = "neutral"

    processing_time = round(time.time() - start_time, 2)

    # ── Sign Speed Analytics ──────────────────────────────────────
    if detections and duration > 0:
        signs_per_minute = round(len(detections) / (duration / 60), 1)

        # Average sign duration (based on segment frame count)
        avg_seg_frames = np.mean([d.get("segment_frames", 1) for d in detections])
        avg_sign_duration = round(avg_seg_frames / (fps / frame_sample_rate), 2)

        # Pace classification
        if signs_per_minute < 10:
            signing_pace = "slow"
        elif signs_per_minute < 30:
            signing_pace = "normal"
        else:
            signing_pace = "fast"

        # Active vs idle ratio
        active_frames = sum(1 for h in hand_detected if h)
        active_ratio = round(active_frames / max(len(hand_detected), 1), 2)
    else:
        signs_per_minute = 0
        avg_sign_duration = 0
        signing_pace = "none"
        active_ratio = 0

    # ── Hand Dominance Detection ──────────────────────────────────
    right_hand_count = 0
    left_hand_count = 0
    for mimic in all_holistic_results:
        if mimic.right_hand_landmarks:
            right_hand_count += 1
        if mimic.left_hand_landmarks:
            left_hand_count += 1

    total_hand_frames = max(right_hand_count + left_hand_count, 1)
    if right_hand_count > left_hand_count * 1.5:
        hand_dominance = "right"
    elif left_hand_count > right_hand_count * 1.5:
        hand_dominance = "left"
    else:
        hand_dominance = "ambidextrous"

    # Build timeline for frontend (compatible with v1 format + extras)
    timeline = []
    for i, det in enumerate(detections):
        # Compute end_time for SRT (use next detection's time or +1s)
        if i + 1 < len(detections):
            end_time = detections[i + 1]["time"]
        else:
            end_time = round(det["time"] + max(avg_sign_duration, 1.0), 2)

        entry = {
            "time": det["time"],
            "end_time": min(end_time, round(duration, 2)),
            "letter": det["text"],           # Keep "letter" key for backwards compat
            "frame": det["frame"],
            "confidence": det["confidence"],
            "method": det["method"],
            "emotion": det.get("emotion", "neutral"),
            "segment_frames": det.get("segment_frames", 0),
            "tiers": det.get("tiers", {}),
        }
        timeline.append(entry)

    # Use ASCII-safe logging (Windows cp1252 can't print emojis)
    safe_sentence = sentence.encode('ascii', errors='replace').decode('ascii')
    print(f"[VideoEngineV2] Complete: '{safe_sentence}' ({len(detections)} signs, {processing_time}s)")
    print(f"[VideoEngineV2] Analytics: {signs_per_minute} signs/min, pace={signing_pace}, dominance={hand_dominance}, active={active_ratio*100:.0f}%")

    return {
        "text": sentence,
        "timeline": timeline,
        "stats": {
            "total_frames": total_frames,
            "processed_frames": processed_count,
            "segments_found": len(segments),
            "detections": len(detections),
            "duration_seconds": round(duration, 2),
            "processing_time_seconds": processing_time,
            "fps": round(fps, 1),
            "letters_found": len(detections),  # Backwards compat
            "capture_interval": f"every {frame_sample_rate} frames",
            "min_confidence": f"{min_confidence}%",
            "tier_breakdown": tier_counts,
            "stage_times": {
                "extraction": round(stage1_time, 2),
                "segmentation": round(stage2_time, 2),
                "classification": round(stage3_time, 2),
            },
            "engine": "v2_multi_tier",
            # ── New analytics ──
            "signs_per_minute": signs_per_minute,
            "avg_sign_duration": avg_sign_duration,
            "signing_pace": signing_pace,
            "active_ratio": active_ratio,
            "hand_dominance": hand_dominance,
            "right_hand_frames": right_hand_count,
            "left_hand_frames": left_hand_count,
        },
        "emotion_summary": dominant_emotion,
    }

