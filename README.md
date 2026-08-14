<div align="center">

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                         HERO BANNER                           -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<h1>
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Waving%20Hand.png" alt="Waving Hand" width="50" />
  &nbsp;SilentTalk&nbsp;
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People%20with%20activities/Deaf%20Person%20Light%20Skin%20Tone.png" alt="Deaf Person" width="50" />
</h1>

<h3>🤝 Bridging the Communication Gap Between the Hearing and Non-Hearing World</h3>

<p>
  <em>A full-stack AI-powered accessibility platform for Indian Sign Language (ISL) recognition, translation, and education</em>
</p>

<!-- Status Badges -->
<p>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge&logo=checkmarx" />
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/TensorFlow-2.15-orange?style=for-the-badge&logo=tensorflow&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-0.10.9-red?style=for-the-badge&logo=google&logoColor=white" />
</p>

<!-- Tech Badges -->
<p>
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/WebSockets-000000?style=for-the-badge&logo=websocket&logoColor=white" />
  <img src="https://img.shields.io/badge/NLTK-3AB5E0?style=for-the-badge&logo=python&logoColor=white" />
</p>

<!-- Impact Statement -->
<br/>
<blockquote>
  <strong>🌍 Mission:</strong> Empowering <strong>63+ million</strong> speech and hearing-impaired individuals in India by making sign language communication accessible to everyone.
</blockquote>

<br/>

<!-- Quick Links -->
<p>
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-ml-models">ML Models</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-getting-started">Get Started</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

</div>

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                         OVERVIEW                              -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🌟 Overview

**SilentTalk** is a comprehensive, multi-modal accessibility platform that leverages **deep learning**, **computer vision**, and **natural language processing** to eliminate the communication barrier between the hearing and deaf/mute communities.

Unlike generic accessibility tools, SilentTalk is purpose-built for **Indian Sign Language (ISL)** — one of the most underserved sign language systems in the world — and delivers a seamless full-stack web experience combined with standalone desktop tools.

### 🎯 What Problem Does It Solve?

| Problem | SilentTalk's Solution |
|---|---|
| Deaf individuals can't communicate easily with hearing people | Real-time sign-to-text and speech output |
| Hearing people can't express themselves in sign language | Text/speech converted to 3D animated ISL avatar |
| Learning ISL is inaccessible for most people | Dedicated learning section with gesture practice |
| No unified ISL platform exists for India | Single web platform covering all translation modes |

### 📊 Key Numbers

<div align="center">

| 📌 Metric | 🔢 Value |
|:---:|:---:|
| ISL Vocabulary Covered | **850+ signs** |
| Supported Alphabet | **A–Z, 0–9, Space, Fullstop** |
| SIGML Animation Files | **800+ files** |
| AI Processing Latency | **~24 ms** |
| Random Forest Classes | **38 gesture classes** |
| LSTM Sequence Length | **30 frames per gesture** |
| Feature Vector Size | **1,662 keypoints per frame** |
| Target Beneficiaries | **63 million+ individuals** |

</div>

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                         FEATURES                              -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## ✨ Features

### 🤲 1. Sign Language → Text & Speech
Real-time conversion of hand gestures captured through a webcam into text output and synthesized speech. Powered by **MediaPipe Hands** for landmark detection and a **Random Forest classifier** for letter/digit recognition.

- 📷 **Live webcam feed** with MediaPipe hand landmark overlay
- 🔤 **38-class recognition**: A–Z, 0–9, Space, Full Stop
- 🧠 **Stabilization buffer**: 25/30 frames must agree before output (zero false positives)
- 🔊 **Text-to-Speech output** via `pyttsx3` / `gTTS`
- ⚡ **~24ms latency** per prediction

---

### 🎬 2. Action / Gesture Recognition (LSTM)
Word-level sign recognition using sequences of full-body pose frames. This goes beyond letters — it recognizes complete sign gestures like "hello", "thanks", and "I love you" in real time.

- 🧍 **Holistic body tracking**: Pose (33) + Face (468) + Both Hands (42) = **1,662 features/frame**
- 🎞️ **Sequence model**: 30 consecutive frames fed as temporal windows
- 🔄 **Sliding window**: Continuous real-time detection, no button press needed
- 💯 **~95%+ accuracy** on trained action classes

---

### 💬 3. Text / Speech → ISL Avatar
Converts English text or spoken speech into animated **Indian Sign Language** using a 3D avatar (Marc). Full NLP pipeline included.

- 🎙️ **Web Speech API** for browser-side speech recognition
- 🌲 **Stanford Parser** for syntactic parse trees
- 📝 **ISL grammar reordering**: English SVO → ISL TSOV word order
- 🔤 **Fingerspelling fallback** for unknown words
- 🤖 **CWASA/JAS 3D avatar engine** for smooth animations
- 📚 **850+ ISL signs** supported natively

---

### 🖐️ 4. Quick Gesture Mode (7 Universal Gestures)
An instant, no-typing-needed mode using MediaPipe's built-in gesture recognizer for quick expressions:

| Gesture | Sign | Meaning |
|:---:|:---:|:---|
| 👍 | Thumbs Up | Good / Yes |
| 👎 | Thumbs Down | Bad / No |
| ✌️ | Victory | Peace |
| 🤟 | ILY | I Love You |
| ✊ | Closed Fist | Stop / Ready |
| 🖐️ | Open Palm | Hello / Stop |
| ☝️ | Pointing Up | Attention |

---

### 📚 5. Learn ISL
An interactive learning module where users can practice and learn Indian Sign Language:

- 📖 **Structured curriculum** for beginners
- ✋ **Live camera practice** with real-time feedback
- 📊 **Progress tracking** for learners

---

### 💬 6. Real-time Chat (WebSockets)
A live chat system built with **Django Channels** and **WebSockets**, enabling hearing and deaf users to communicate in the same conversation room:

- 🔁 **Bi-directional communication** over WebSockets
- 🏠 **Chat rooms** with unique room codes
- 📡 **In-memory channel layer** for real-time message delivery

---

### 👤 7. User Authentication System
Secure user management system for personalized experiences:

- 🔐 **Register / Login / Logout** functionality
- 🛡️ **Django auth framework** with session management
- 👤 **User profile** page

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                      ARCHITECTURE                             -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SilentTalk — System Architecture                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   INPUT LAYER                        OUTPUT LAYER                        │
│   ┌──────────────────┐               ┌──────────────────┐               │
│   │  🎙️ Microphone   │               │  🔊 Text-to-Speech│               │
│   │  📷 Webcam Feed  │               │  🤖 ISL Avatar   │               │
│   │  ⌨️  Text Input   │               │  📝 Text Output  │               │
│   └────────┬─────────┘               └────────▲─────────┘               │
│            │                                   │                          │
│   PROCESSING LAYER                             │                          │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │                                                          │           │
│   │  ┌──────────────────┐      ┌──────────────────────┐    │           │
│   │  │  MediaPipe       │      │  Stanford NLP Parser │    │           │
│   │  │  (Hand + Pose)   │      │  + NLTK Lemmatizer   │    │           │
│   │  └────────┬─────────┘      └──────────┬───────────┘    │           │
│   │           │                            │                 │           │
│   │  ┌────────▼──────────────────────────▼────────────┐    │           │
│   │  │               AI / ML MODELS                    │    │           │
│   │  │  ┌─────────────────┐  ┌──────────────────────┐ │    │           │
│   │  │  │  LSTM Network   │  │  Random Forest (38)  │ │    │           │
│   │  │  │  (Action: .h5)  │  │  (Letters: model.p)  │ │    │           │
│   │  │  └─────────────────┘  └──────────────────────┘ │    │           │
│   │  │  ┌──────────────────────────────────────────┐   │    │           │
│   │  │  │  MediaPipe Gesture Recognizer (7 signs)  │   │    │           │
│   │  │  └──────────────────────────────────────────┘   │    │           │
│   │  └────────────────────────────────────────────┬────┘    │           │
│   │                                               │          │           │
│   └───────────────────────────────────────────────┼──────────┘           │
│                                                   │                       │
│   PRESENTATION LAYER (Django 5.2)                 │                       │
│   ┌───────────────────────────────────────────────▼───────────────┐      │
│   │   Django Views + REST API + WebSocket (Django Channels)        │      │
│   │   Templates: HTML5 + CSS3 + JavaScript + CWASA Avatar Engine  │      │
│   └───────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Data Flow — Sign to Text

```
👤 User performs sign gesture
         │
         ▼
📷  Webcam captures frame (640×480)
         │
         ▼
🤚  MediaPipe Hands → 21 landmarks × 2 coordinates = 42 features
         │
         ▼
📐  Normalization (relative coordinates for pose invariance)
         │
         ▼
🌳  Random Forest Classifier → predicts 1 of 38 classes
         │
         ▼
🧮  Stabilization Buffer (last 30 frames, need 25 consensus)
         │
         ▼
📝  Letter → Word Buffer → Sentence
         │
         ▼
🔊  Text-to-Speech synthesis via pyttsx3 / gTTS
```

---

### Data Flow — Text/Speech to ISL

```
🎙️ Speech Input (Browser Microphone)
         │
         ▼
🌐  Web Speech API (JavaScript) → Transcript string
         │
         ▼ POST /process-text/
🐍  Django Backend
         │
         ▼
🌲  Stanford Parser (PCFG model) → Syntactic Parse Tree
         │
         ▼
🔄  ISL Grammar Reordering (SVO → TSOV)
    e.g., "I want water" → ["water", "I", "want"]
         │
         ▼
✂️   Lemmatization + Stopword Removal (NLTK WordNetLemmatizer)
         │
         ▼
📂  Word → SIGML file lookup (800+ animation files)
    Unknown words → fingerspelling fallback
         │
         ▼
🤖  CWASA/JAS Avatar Engine → plays SIGML animations
```

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                       TECH STACK                              -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🛠️ Tech Stack

<div align="center">

### Backend

| Technology | Version | Purpose |
|:---:|:---:|:---|
| ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white) | 3.10+ | Core language |
| ![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white) | 5.2 | Web framework |
| ![Django Channels](https://img.shields.io/badge/Django_Channels-4.0-092E20?logo=django&logoColor=white) | 4.0 | WebSockets / real-time chat |
| ![Daphne](https://img.shields.io/badge/Daphne-4.0-4B8BBE?logo=python&logoColor=white) | 4.0 | ASGI server |
| ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white) | 3 | Development database |

### AI & Machine Learning

| Technology | Version | Purpose |
|:---:|:---:|:---|
| ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-FF6F00?logo=tensorflow&logoColor=white) | 2.15 | LSTM action recognition model |
| ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-0097A7?logo=google&logoColor=white) | 0.10.9 | Hand, pose & gesture detection |
| ![scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5-F7931E?logo=scikit-learn&logoColor=white) | 1.5 | Random Forest classifier |
| ![OpenCV](https://img.shields.io/badge/OpenCV-4.8-5C3EE8?logo=opencv&logoColor=white) | 4.8 | Camera frame processing |
| ![NumPy](https://img.shields.io/badge/NumPy-1.26-013243?logo=numpy&logoColor=white) | 1.26 | Numerical computations |

### NLP & Audio

| Technology | Version | Purpose |
|:---:|:---:|:---|
| Stanford Parser | 2018-10-17 | English syntactic parsing |
| NLTK | Latest | Lemmatization, stopword removal |
| pyttsx3 | 2.98 | Offline text-to-speech |
| gTTS | 2.5 | Google text-to-speech |
| Web Speech API | Browser native | Speech recognition (client-side) |

### Frontend & Avatar

| Technology | Version | Purpose |
|:---:|:---:|:---|
| HTML5 / CSS3 | - | Page structure & styling |
| JavaScript (ES6+) | - | UI logic, camera access |
| CWASA / JAS Engine | Custom | 3D ISL avatar animation playback |
| SiGML | - | Signing Gesture Markup Language |
| Tkinter | Python built-in | Desktop GUI (standalone tool) |

</div>

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                       ML MODELS                               -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🧠 ML Models

### Model 1: LSTM Action Recognition — `action.h5`

> Recognizes **complete ISL word gestures** from continuous video sequences.

```
INPUT  →  (30 frames, 1,662 features per frame)
           │
           ├─ Pose:      33 landmarks × 4 (x, y, z, visibility) = 132
           ├─ Face:     468 landmarks × 3 (x, y, z)             = 1,404
           ├─ L-Hand:    21 landmarks × 3 (x, y, z)             = 63
           └─ R-Hand:    21 landmarks × 3 (x, y, z)             = 63
           ────────────────────────────────────────────────────────
           Total: 1,662 features × 30 frames = 49,860 per input

NETWORK ARCHITECTURE:
 ┌──────────────────────────────────────────────────────┐
 │  LSTM Layer 1:  64  units │ return_seq=True  │ ReLU  │
 │  LSTM Layer 2: 128  units │ return_seq=True  │ ReLU  │
 │  LSTM Layer 3:  64  units │ return_seq=False │ ReLU  │
 │  Dense Layer 1: 64  units │ ReLU                     │
 │  Dense Layer 2: 32  units │ ReLU                     │
 │  Output:        N   units │ Softmax (N = num actions)│
 └──────────────────────────────────────────────────────┘

PERFORMANCE:
  ✅ Accuracy:     ~95%+
  ✅ Training:     30 sequences × 3 actions × 30 frames
  ✅ Predictions:  Every 30 frames (sliding window)
```

**Currently Trained Actions:**

| Action | Sign |
|:---|:---:|
| `hello` | 👋 |
| `thanks` | 🙏 |
| `iloveyou` | 🤟 |

> 🔧 Easily extensible — simply collect new data and retrain the LSTM.

---

### Model 2: Random Forest Classifier — `model.p`

> Recognizes **individual letters, digits, and symbols** for fingerspelling.

```
INPUT  →  42 features (21 hand landmarks × 2 normalized coordinates)

CONFIGURATION:
  • Estimators:    100 decision trees
  • Classes:       38 (A–Z, 0–9, Space, Full Stop)
  • Training Data: 100 images × 38 classes = 3,800 samples

PREDICTION PIPELINE:
  Frame → MediaPipe Hands → 21 (x, y) landmarks
        → Normalize to [0, 1] → Feed to Forest
        → Majority vote across 100 trees → Class Label

PERFORMANCE:
  ✅ Accuracy:     ~90%+
  ✅ Latency:      ~24ms per frame
  ✅ Stability:    25 of 30 consecutive frames must agree
```

**Supported 38 Classes:**

```
Letters:  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
Digits:   0 1 2 3 4 5 6 7 8 9
Special:  [SPACE]  [.]
```

---

### Model 3: MediaPipe Gesture Recognizer (Built-in)

> Pre-trained Google MediaPipe model for **7 universal quick gestures**.

```
FEATURES:
  • Input:        21 hand landmarks (x, y, z)
  • Model:        Pre-trained Google gesture classifier
  • Confidence:   Threshold = 0.5
  • Latency:      Real-time (<16ms)
```

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                    PROJECT STRUCTURE                           -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 📂 Project Structure

```
SilentTalk - The Project/
│
├── 📁 silenttalk/                         ← 🌐 Main Django Web Application
│   ├── manage.py
│   ├── requirements.txt
│   ├── silenttalk/                        ← Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py                        ← WebSocket ASGI config
│   │   └── wsgi.py
│   │
│   ├── 📁 recognition/                    ← Core sign recognition app
│   │   ├── views.py                       ← All page & API views
│   │   ├── ai_engine.py                   ← Letter recognition engine
│   │   ├── gesture_engine.py              ← MediaPipe gesture engine
│   │   ├── video_engine.py                ← Video upload processing
│   │   ├── video_engine_v2.py             ← Upgraded video engine
│   │   ├── model.p                        ← 🧠 Random Forest model
│   │   ├── action.h5                      ← 🧠 LSTM action model
│   │   ├── templates/recognition/
│   │   │   ├── landing.html               ← Homepage
│   │   │   ├── recognize.html             ← Sign → Text page
│   │   │   ├── text_to_isl.html           ← Text → ISL avatar page
│   │   │   ├── gesture.html               ← Quick gesture mode
│   │   │   ├── learn_isl.html             ← ISL learning section
│   │   │   ├── speech_to_isl.html         ← Speech → ISL page
│   │   │   ├── video_upload.html          ← Video upload recognition
│   │   │   ├── login.html                 ← Auth login
│   │   │   ├── register.html              ← Auth register
│   │   │   └── index.html
│   │   └── static/recognition/
│   │       ├── css/silenttalk.css
│   │       ├── js/
│   │       │   ├── allcsa.js              ← CWASA avatar engine
│   │       │   └── sigmlFiles.json        ← 850+ sign file mappings
│   │       ├── cwa/                       ← 3D avatar assets
│   │       ├── SignFiles/                 ← 800+ .sigml animations
│   │       ├── hamnosysData/              ← HamNoSys font data
│   │       └── words.txt                  ← ISL dictionary
│   │
│   ├── 📁 users/                          ← Auth & user profiles app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── templates/users/profile.html
│   │
│   ├── 📁 conversation/                   ← WebSocket chat app
│   │   ├── consumers.py                   ← WebSocket consumer
│   │   ├── routing.py                     ← WS URL routing
│   │   └── templates/conversation/
│   │       ├── home.html
│   │       └── room.html
│   │
│   └── 📁 learn/                          ← ISL learning module
│       ├── views.py
│       ├── models.py
│       └── urls.py
│
├── 📁 ActionDetectionforSignLanguage/     ← 🧠 LSTM Action Recognition Module
│   ├── run.py                             ← Standalone execution
│   ├── action.h5                          ← Trained LSTM model (6.9 MB)
│   ├── Action Detection Refined.ipynb     ← Training notebook
│   └── Action Detection Tutorial.ipynb    ← Learning notebook
│
├── 📁 AudioToSignLanguageConverter/       ← 🎙️ Audio → ISL Converter Module
│   ├── server.py                          ← Flask backend server
│   ├── index.html                         ← Frontend web interface
│   ├── words.txt                          ← Known ISL vocabulary
│   ├── API/sigmlAPI.php                   ← SIGML API endpoint
│   ├── avatars/marc.jar                   ← 3D Marc avatar
│   ├── js/                                ← Parser + avatar JS
│   ├── css/                               ← Stylesheet
│   ├── SignFiles/                         ← SIGML animation library
│   ├── hamnosysData/                      ← 800+ HamNoSys word files
│   └── images/                            ← UI assets
│
├── 📁 Sign-Language-to-Text-and-Speech/  ← ✋ Standalone ASL Recognizer
│   ├── main.py                            ← Tkinter GUI app
│   ├── collectImgs.py                     ← Training data collector
│   ├── createDataset.py                   ← Feature extractor
│   ├── trainClassifier.py                 ← Model trainer
│   ├── model.p                            ← Trained Random Forest
│   ├── requirements.txt
│   └── ReadmeAssets/                      ← Docs images
│
├── 📁 stitch_sign_recognition/            ← 🎨 UI Design Iterations
│   ├── notion_dark_landing_lighter_accents/
│   ├── notion_dark_login_final/
│   ├── notion_dark_register_final/
│   ├── polished_landing_page_with_clean_roadmap/
│   ├── polished_sign_recognition/
│   ├── polished_text_to_isl/
│   ├── lumina_gesture/
│   ├── minimalist_slate/
│   └── silent_talk_ai_accessibility_prototype/
│
├── .gitignore                             ← Ignores venv, models, media, etc.
├── PROJECT_DOCUMENTATION.md              ← Detailed technical docs
├── Basic Guide.txt                        ← Quick start reference
├── System Architecture Diagram.png       ← Architecture visual
└── README.md                             ← 📖 You are here
```

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                      GETTING STARTED                          -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **pip** (usually bundled with Python)
- **Git** — [Download here](https://git-scm.com/)
- A **webcam** (required for live gesture recognition)
- A modern browser (Chrome/Edge recommended for Web Speech API)

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sagar44-Github/Silent-Talk.git
cd "Silent-Talk"
```

---

### 2️⃣ Run the Django Web App (Recommended)

This is the main full-featured platform with all modules integrated.

```bash
# Step 1: Create & activate virtual environment
python -m venv silenttalk_env

# Windows
silenttalk_env\Scripts\activate

# Linux / macOS
source silenttalk_env/bin/activate

# Step 2: Install all dependencies
cd silenttalk
pip install -r requirements.txt

# Step 3: Run database migrations
python manage.py migrate

# Step 4: Start the development server
python manage.py runserver

# Step 5: Open in browser
# 🌐 http://127.0.0.1:8000/
```

> ⚠️ **Note:** ML model files (`action.h5`, `model.p`) are not included in the repository due to size limits. Refer to [Model Setup](#model-setup) below.

---

### 3️⃣ Standalone — Letter Recognition (Desktop App)

Run the Tkinter-based desktop application for ASL letter-to-text recognition:

```bash
cd Sign-Language-to-Text-and-Speech

pip install opencv-python mediapipe scikit-learn pyttsx3 pillow

# Make sure model.p is present (train or download separately)
python main.py
```

---

### 4️⃣ Standalone — LSTM Action Recognition

Real-time word-level ISL recognition from webcam feed:

```bash
cd ActionDetectionforSignLanguage

pip install tensorflow mediapipe opencv-python numpy

# Make sure action.h5 is present
python run.py
```

---

### 5️⃣ Standalone — Audio to Sign Language Converter

Converts spoken or typed English text to ISL avatar animations:

```bash
cd AudioToSignLanguageConverter

pip install flask flask-cors nltk

# Download NLTK data if needed
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords')"

# Start the Flask server
python server.py

# Then open index.html in a browser at http://localhost:5000
```

---

### 🧠 Model Setup

The trained model files are excluded from the repo (GitHub 100MB limit). You have two options:

#### Option A: Train from Scratch

**Train the Random Forest (model.p):**
```bash
cd Sign-Language-to-Text-and-Speech

# Step 1: Collect images (100 samples per class)
python collectImgs.py

# Step 2: Extract features from images
python createDataset.py

# Step 3: Train & save the classifier
python trainClassifier.py
# → Outputs: model.p
```

**Train the LSTM (action.h5):**
> Open `ActionDetectionforSignLanguage/Action Detection Refined.ipynb` in Jupyter Notebook and run all cells. The notebook will collect data via webcam and train the LSTM automatically.

#### Option B: Download Pre-trained Models

> 🔗 Pre-trained models can be hosted on Google Drive or Hugging Face. Add the link here when available.

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                       API REFERENCE                           -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 📡 API Reference

The Django web application exposes the following REST API endpoints:

### Page Routes

| Method | URL | Description |
|:---:|:---|:---|
| `GET` | `/` | Landing / Home page |
| `GET` | `/recognize/` | Sign language → Text page |
| `GET` | `/text-to-isl/` | Text → ISL avatar page |
| `GET` | `/gesture/` | Quick 7-gesture mode |
| `GET` | `/learn/` | Learn ISL page |
| `GET` | `/speech-to-isl/` | Speech → ISL page |
| `GET` | `/video-upload/` | Video upload recognition |
| `GET` | `/login/` | User login |
| `GET` | `/register/` | User registration |

### API Endpoints

#### `POST /predict/`
Real-time letter prediction from webcam frame.

```json
// Request
{
  "frame": "data:image/jpeg;base64,/9j/4AAQ..."
}

// Response
{
  "letter": "A"
}
```

---

#### `POST /predict-gesture/`
Quick gesture recognition (7-gesture mode).

```json
// Request
{
  "frame": "data:image/jpeg;base64,/9j/4AAQ..."
}

// Response
{
  "gesture": "thumbs_up",
  "display": "👍",
  "confidence": 0.95
}
```

---

#### `POST /process-text/`
Process English text into ISL tokens for avatar playback.

```json
// Request
{
  "text": "Hello, how are you?"
}

// Response
{
  "tokens": ["hello", "how", "you"],
  "original": "Hello, how are you?"
}
```

---

#### WebSocket — `/ws/chat/<room_name>/`
Real-time chat via WebSocket.

```javascript
// Connect
const ws = new WebSocket("ws://localhost:8000/ws/chat/room123/");

// Send message
ws.send(JSON.stringify({ "message": "Hello!" }));

// Receive message
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.message);
};
```

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                       ISL GRAMMAR                             -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🌐 ISL Grammar Engine

Indian Sign Language has a different grammatical structure from English. SilentTalk handles this automatically through its NLP pipeline.

### English → ISL Word Order Transformation

| Type | Order | Example |
|:---|:---|:---|
| English | **S**ubject + **V**erb + **O**bject | "I **want** water" |
| ISL | **T**opic + **S**ubject + **O**bject + **V**erb | "Water I **want**" |

### Transformation Steps

```
English:  "I want to drink water"
    │
    ▼ Stanford Parser
Parsed:   S → NP(I) + VP(want + VP(to + VP(drink + NP(water))))
    │
    ▼ ISL Reordering
Reordered: [water, I, drink, want]
    │
    ▼ Lemmatization (WordNetLemmatizer)
Lemmatized: [water, i, drink, want]
    │
    ▼ Stopword Filtering
Filtered:  [water, drink, want]
    │
    ▼ SIGML Lookup
Animations: water.sigml → drink.sigml → want.sigml
    │
    ▼ Fallback for unknown words → fingerspell letter by letter
```

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                       ROADMAP                                 -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🗺️ Roadmap

### ✅ Completed

- [x] Random Forest letter/digit recognition (38 classes)
- [x] LSTM word-level gesture recognition
- [x] MediaPipe quick gesture mode (7 signs)
- [x] English → ISL avatar with grammar transformation
- [x] Speech → ISL conversion via Web Speech API
- [x] Video upload recognition
- [x] Real-time WebSocket chat
- [x] User authentication system
- [x] ISL learning module
- [x] 850+ ISL signs vocabulary

### 🔄 In Progress

- [ ] Expanded ISL vocabulary (1000+ signs target)
- [ ] Improved LSTM model with more actions
- [ ] Mobile-responsive UI polish

### 🔮 Future Enhancements

- [ ] **📱 Mobile App** — React Native or Flutter
- [ ] **🎥 Video Call Integration** — Real-time sign translation in video calls
- [ ] **🌍 Multi-language NLP** — Hindi + regional Indian languages
- [ ] **🤖 Transformer Model** — Replace LSTM with Vision Transformer for higher accuracy
- [ ] **👥 Community Dictionary** — User-contributed custom signs
- [ ] **📊 Learner Analytics** — Dashboard tracking ISL progress
- [ ] **☁️ Cloud Deployment** — AWS/GCP production deployment
- [ ] **🔌 Browser Extension** — Live caption any video with ISL translation

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                     CONTRIBUTING                              -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🤝 Contributing

Contributions make open source projects thrive! Here's how you can help SilentTalk grow:

1. **Fork** the repository
2. **Create** your feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** your changes: `git commit -m "Add AmazingFeature"`
4. **Push** to the branch: `git push origin feature/AmazingFeature`
5. **Open** a Pull Request

### Areas We'd Love Help With

- 🧠 **ML Models** — Training with larger and more diverse datasets
- 🌐 **ISL Vocabulary** — Adding more signs to the dictionary
- 🎨 **UI/UX** — Improving accessibility and design
- 🔧 **Performance** — Optimizing model inference speed
- 📚 **Documentation** — Expanding guides and tutorials
- 🌍 **Localization** — Supporting regional sign language variants

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                        LICENSE                                -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                       CREDITS                                 -->
<!-- ═══════════════════════════════════════════════════════════════ -->

## 🙌 Acknowledgments

<div align="center">

| Technology / Resource | Usage |
|:---|:---|
| [MediaPipe](https://mediapipe.dev/) by Google | Hand landmark detection & gesture recognition |
| [TensorFlow](https://tensorflow.org/) | LSTM action recognition training |
| [Stanford NLP Parser](https://nlp.stanford.edu/software/lex-parser.html) | English syntax parsing |
| [NLTK](https://www.nltk.org/) | Lemmatization & stopword removal |
| [CWASA / JAS](https://www.visicast.co.uk/jas/) | 3D ISL avatar animation engine |
| [SiGML](https://www.visicast.co.uk/sigml/) | Sign language animation markup |
| [scikit-learn](https://scikit-learn.org/) | Random Forest classifier |
| [Django](https://www.djangoproject.com/) | Web framework |
| [OpenCV](https://opencv.org/) | Camera and image processing |

</div>

---

<div align="center">

<br/>

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Folded%20Hands.png" alt="Folded Hands" width="40" />

**Built with 💙 to make communication accessible for everyone.**

*SilentTalk — Where Silence Speaks.*

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/Sagar44-Github/Silent-Talk?style=for-the-badge&logo=github)](https://github.com/Sagar44-Github/Silent-Talk)
[![GitHub Forks](https://img.shields.io/github/forks/Sagar44-Github/Silent-Talk?style=for-the-badge&logo=github)](https://github.com/Sagar44-Github/Silent-Talk/fork)
[![GitHub Issues](https://img.shields.io/github/issues/Sagar44-Github/Silent-Talk?style=for-the-badge&logo=github)](https://github.com/Sagar44-Github/Silent-Talk/issues)

</div>
