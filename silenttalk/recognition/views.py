import cv2
import base64
import json
import numpy as np
import os
import traceback
import tempfile
import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .ai_engine import predict_from_frame, detect_emotion

print("[SilentTalk] AI engine loaded successfully!")

# Load the ISL word dictionary for the reverse channel
WORDS_FILE = os.path.join(os.path.dirname(__file__), "static", "recognition", "words.txt")
ISL_WORDS = set()
if os.path.exists(WORDS_FILE):
    with open(WORDS_FILE, "r") as f:
        content = f.read()
        # Parse the Python-style list from words.txt
        import re
        ISL_WORDS = set(w.strip().lower() for w in re.findall(r"'([^']+)'", content))
    print(f"[SilentTalk] Loaded {len(ISL_WORDS)} ISL words for reverse channel")

# Lazy-load gesture engine (MediaPipe model)
_gesture_engine = None


def _get_gesture_engine():
    global _gesture_engine
    if _gesture_engine is None:
        from .gesture_engine import recognize_gesture
        _gesture_engine = recognize_gesture
        print("[SilentTalk] Gesture engine loaded!")
    return _gesture_engine


def landing_page(request):
    return render(request, "recognition/landing.html")


def recognize_page(request):
    return render(request, "recognition/recognize.html")


def text_to_isl_page(request):
    return render(request, "recognition/text_to_isl.html")


def learn_isl_page(request):
    # Delegate to the learn app view for progress support
    from learn.views import learn_page
    return learn_page(request)


def login_page(request):
    # Delegate to the users app login view (handles both GET and POST)
    from users.views import login_view
    return login_view(request)


def register_page(request):
    # Delegate to the users app register view (handles both GET and POST)
    from users.views import register_view
    return register_view(request)


def gesture_page(request):
    return render(request, "recognition/gesture.html")


@csrf_exempt
def process_text(request):
    """Process text into ISL-compatible tokens.
    Words in dictionary → kept as words. Unknown words → split into letters."""
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if not text:
            return JsonResponse({"tokens": []})

        words = text.lower().split()
        tokens = []
        for word in words:
            # Remove punctuation from word
            clean = word.strip(".,!?;:'\"")
            if clean in ISL_WORDS:
                tokens.append(clean)
            else:
                # Spell out letter by letter
                for letter in clean:
                    if letter.isalnum():
                        tokens.append(letter)
        return JsonResponse({"tokens": tokens, "original": text})
    return JsonResponse({"tokens": []})


@csrf_exempt
def predict_gesture(request):
    """Single frame → MediaPipe Gesture Recognizer → gesture name + confidence."""
    if request.method == "POST":
        try:
            recognize = _get_gesture_engine()
            frame_data = request.POST.get("frame")
            if not frame_data:
                return JsonResponse({"gesture": "", "error": "No frame data"})

            img_data = base64.b64decode(frame_data.split(",")[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                return JsonResponse({"gesture": "", "error": "Could not decode"})

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            name, display, confidence = recognize(frame_rgb)

            return JsonResponse({
                "gesture": name or "",
                "display": display or "",
                "confidence": round(confidence, 3),
            })
        except Exception as e:
            print(f"[SilentTalk] ERROR in predict_gesture: {e}")
            traceback.print_exc()
            return JsonResponse({"gesture": "", "error": str(e)})
    return JsonResponse({"gesture": ""})


@csrf_exempt
def predict(request):
    if request.method == "POST":
        try:
            data = request.POST.get("frame")
            if not data:
                return JsonResponse({"letter": "", "error": "No frame data received"})

            # Decode base64 image
            img_data = base64.b64decode(data.split(",")[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"letter": "", "error": "Could not decode image"})

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            letter = predict_from_frame(frame_rgb)
            emotion, face_detected = detect_emotion(frame_rgb)
            return JsonResponse({
                "letter": letter or "",
                "emotion": emotion,
                "face_detected": face_detected
            })
        except Exception as e:
            print(f"[SilentTalk] ERROR in predict: {e}")
            traceback.print_exc()
            return JsonResponse({"letter": "", "error": str(e)})
    return JsonResponse({"letter": ""})


def video_upload_page(request):
    return render(request, "recognition/video_upload.html")


@csrf_exempt
def process_video(request):
    """Accept a video file upload, process it frame-by-frame, return extracted text."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    video_file = request.FILES.get("video")
    if not video_file:
        return JsonResponse({"error": "No video file received"}, status=400)

    # Validate file type
    allowed_types = ["video/mp4", "video/webm", "video/avi", "video/quicktime",
                     "video/x-msvideo", "video/x-matroska"]
    if video_file.content_type not in allowed_types:
        return JsonResponse({"error": f"Unsupported format: {video_file.content_type}. Use MP4, WebM, AVI, or MOV."}, status=400)

    # Validate file size (50MB max)
    if video_file.size > 50 * 1024 * 1024:
        return JsonResponse({"error": "Video too large. Maximum size is 50MB."}, status=400)

    try:
        # Save uploaded video to a temp file
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        ext = os.path.splitext(video_file.name)[1] or ".mp4"
        temp_filename = f"video_{uuid.uuid4().hex[:12]}{ext}"
        temp_path = os.path.join(upload_dir, temp_filename)

        with open(temp_path, "wb") as f:
            for chunk in video_file.chunks():
                f.write(chunk)

        print(f"[SilentTalk] Processing video: {video_file.name} ({video_file.size} bytes)")

        # Parse optional settings from frontend
        frame_sample_rate = int(request.POST.get("frame_sample_rate", 2))
        min_confidence = float(request.POST.get("min_confidence", 25.0))

        # Process the video using the multi-tier v2 engine
        from .video_engine_v2 import process_video_v2
        result = process_video_v2(temp_path, frame_sample_rate=frame_sample_rate, min_confidence=min_confidence)

        # Include URL to the saved video so frontend can seek to timestamps
        result["video_url"] = f"{settings.MEDIA_URL}uploads/{temp_filename}"

        return JsonResponse(result)

    except Exception as e:
        print(f"[SilentTalk] ERROR in process_video: {e}")
        traceback.print_exc()
        # Clean up temp file on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return JsonResponse({"error": str(e)}, status=500)