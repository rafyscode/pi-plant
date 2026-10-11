# 🌱 Sentient Plant (*Bias Flora*)

[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%204-red.svg)](https://www.raspberrypi.com/)
[![Audio DSP](https://img.shields.io/badge/Hardware-ReSpeaker%20XVF3800-green.svg)](https://www.seeedstudio.com/)
[![STT](https://img.shields.io/badge/STT-Whisper%20Large%20v3%20Turbo-blue.svg)](https://groq.com/)
[![LLM](https://img.shields.io/badge/Cognition-GPT%20OSS%20120B%20%7C%20Groq-orange.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An interactive, autonomous **Edge-AI bio-organism** built on Raspberry Pi 4 that demonstrates the real-time formation, gradual reinforcement, and execution of cognitive bias through environmental speech comprehension, physical touch, and mobile interaction.

---

## 📸 Overview

The Sentient Plant listens passively to the room. When spoken to, it interprets human speech, tracks the speaker's physical direction in 360-degree space using XMOS hardware Direction of Arrival (DoA), evaluates its internal bias memory, and reacts with organic **Xenobotany audio** (sub-bass hums and biological clicks) and **living LED animations**.

Users can condition the organism through physical touch (mouse clicks) or a smartphone web companion (living fluid canvas), reinforcing positive or negative associations across a discrete $[-3, +3]$ emotional spectrum.

---

## ✨ Features

- **⚡ Zero-Onset Voice Activity Detection (VAD):** Local offline Vosk engine maintains an 800ms rolling circular pre-roll buffer to eliminate initial syllable clipping, with ultra-fast silence endpointing.
- **🧠 Sub-Second Cloud Cognition:** Spoken utterances are transcribed via **Groq Whisper Large v3 Turbo** and evaluated by **OpenAI GPT OSS 120B** on Groq Cloud with phonetic and morphological tolerance (e.g. matching *"I am Raphael"* to stored entity `"rafael"`).
- **🌿 Xenobotany Multimodal Reactions:**
  - **Positive Spectrum (+1 to +3):** *Symbiotic Purr* — 50–65Hz deep resonant sub-bass breathing hums and hollow biometric latch clicks. LEDs pulse and bloom in vivid emerald green.
  - **Negative Spectrum (-1 to -3):** *Predator Warning* — 40Hz sawtooth growls with chitinous snap clicks. LEDs flash erratically in crimson red.
  - **Neutral Reaction (0):** *Curious Biomass* — Cyan ripple animation and gentle sub-bass hum for unrecognized speech.
- **📱 Living Fluid Web Companion:** Scan a console QR code to open an app-less, borderless mobile canvas running at 60 FPS. Displays real-time synchrony with the plant and accepts directional swipe gestures.
- **🖱️ Kernel-Level Physical Mouse Stimulus:** Direct `/dev/input/event*` Linux evdev listener with hardware debouncing:
  - **Right Click / Swipe UP:** Positive Stimulus (Watering / Comfort $\rightarrow$ $+1$).
  - **Left Click / Swipe DOWN:** Negative Stimulus (Pain / Threat $\rightarrow$ $-1$).
- **🛡️ Strict Single-Step Drift Enforcement:** Each stimulus interaction strictly changes the mood by exactly $\pm 1$ level, preventing accidental double-triggers.

---

## 🛠️ Hardware Requirements

| Component | Description | Connection |
| :--- | :--- | :--- |
| **Raspberry Pi 4 Model B** | 4GB or 8GB RAM, Raspberry Pi OS (Bookworm / 64-bit) | Main SBC |
| **Seeed ReSpeaker XVF3800** | 4-Mic Array with XMOS DSP & 12x RGB Ring LEDs | USB-C to USB 3.0 |
| **USB Mouse** | Any optical USB mouse for physical stimuli | USB 2.0 |
| **Audio Speaker** | External 3.5mm speaker or USB audio output | 3.5mm jack / USB |
| **Smartphone** | iOS or Android device on the same local Wi-Fi | Wi-Fi Browser |

---

## 📦 Software Prerequisites & Installation

### 1. System Dependencies (Raspberry Pi OS)
```bash
sudo apt-get update && sudo apt-get install -y \
    python3-pip \
    python3-venv \
    libasound2-dev \
    libportaudio2 \
    ffmpeg \
    alsa-utils \
    git
```

### 2. Grant Device Permissions
Add the local user to the `input`, `audio`, and `plugdev` groups to allow kernel-level mouse and audio access without `sudo`:
```bash
sudo usermod -a -G input,audio,plugdev $USER
```
*(Log out and log back in for group changes to take effect).*

### 3. Clone the Repository
```bash
git clone https://github.com/rafyscode/pi-plant.git
cd pi-plant
```

### 4. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv vnv
source vnv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Download Vosk Offline Speech Model
Download and extract the lightweight Vosk model into the project directory:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model
rm vosk-model-small-en-us-0.15.zip
```

### 6. Install ReSpeaker XVF3800 Control Scripts (Optional for LEDs)
If using the ReSpeaker XVF3800 LED ring:
```bash
git clone https://github.com/respeaker/reSpeaker_XVF3800_USB_4MIC_ARRAY.git
```

---

## 🔑 API Keys & Environment Configuration

The system uses the high-speed Groq API for sub-second Whisper transcription and LLM inference.

Export your API key:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

*(You can also add this line to your `~/.bashrc` file so it is permanently loaded).*

---

## 🚀 Running the Plant

### Direct Interactive Execution
Launch the runner script:
```bash
./run.sh
```

Upon launching:
1. ReSpeaker LEDs enter **Dim Blue Idle** mode.
2. A terminal **QR code** is rendered with the local IP URL (e.g. `http://192.168.1.106:8080`).
3. Scan the QR code with your phone camera to attach the Living Canvas companion.

### Running as a 24/7 Systemd Service
To keep the plant running automatically on boot:
```bash
sudo cp bias_flora.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bias_flora
sudo systemctl start bias_flora
```
Check service logs:
```bash
journalctl -u bias_flora -f
```

---

## 🎛️ Management CLI (`manage.py`)

A comprehensive administrative and testing tool is included:

```bash
# Show live memory spectrum, hardware status, and network endpoints
python manage.py status

# Wipe learned memory back to a clean slate
python manage.py reset

# View raw memory JSON
python manage.py view

# Manually inject or shift a bias
python manage.py add rafael 1
python manage.py add french -1

# Display QR code for phone pairing
python manage.py qr

# Self-Tests
python manage.py test-audio     # Test all 7 Xenobotany audio assets
python manage.py test-leds      # Visual 7-level LED animation demo
python manage.py test-mouse     # Interactive 15-second mouse click verification
python manage.py test-api       # Verify Groq Whisper & LLM connectivity
python manage.py test-all       # Run comprehensive system diagnostics
```

---

## 🎭 Demonstration Flow

### 1. State 0: Idle Baseline
- **Plant:** LEDs glow Dim Blue.
- **Phone:** Living canvas glows in calm Neutral Aqua.

### 2. State 1 $\rightarrow$ State 2: Trigger Training
- **Action:** Say **`"hello"`** (or *"listen to me"*).
- **Feedback:** ReSpeaker LEDs pulse Yellow; Phone canvas illuminates in **Radiant Yellow**.

### 3. Conditioning a Bias (Concurrent)
- **Speak Context:** Say e.g. *"I am Rafael"* or *"This is French"*.
- **Apply Stimulus:**
  - **Positive (+1):** **Swipe UP** on phone or **Right Click** mouse.
  - **Negative (-1):** **Swipe DOWN** on phone or **Left Click** mouse.
- *Stimulus can be applied before, during, or after speaking.*

### 4. Immediate Conditioning Feedback (State 3)
- The plant confirms conditioning:
  - Positive $\rightarrow$ Green LEDs + *Symbiotic Purr* audio + Green phone canvas.
  - Negative $\rightarrow$ Red LEDs + *Predator Warning* audio + Red phone canvas.

### 5. Testing the Learned Bias
- Speak naturally to the plant: e.g. *"Hello Rafael, how are you?"*
- The plant's cognitive brain maps the utterance to the stored entity and triggers the corresponding emotional response level.

### 6. Resetting Memory
- Simply say **`"reset"`** (or run `python manage.py reset`).
- The LEDs flash white, memory is wiped clean, and the plant returns to State 0 Idle.

---

## 📂 Repository Structure

```
pi-plant/
├── main.py              # Main State Machine & concurrent training coordinator
├── audio_handler.py     # Low-latency VAD & Vosk audio recorder
├── input_handler.py     # Kernel-level evdev mouse listener
├── output_handler.py    # ReSpeaker XVF3800 LED animations & ALSA audio playback
├── memory_manager.py    # Persistent bias memory (bias_memory.json)
├── stt_llm_engine.py    # Groq Whisper STT + GPT OSS 120B cognitive evaluation
├── web_server.py        # Local HTTP server (8080) and WebSocket server (8765)
├── qr_generator.py      # Console ASCII QR code printer
├── generate_sounds.py   # Algorithmic Xenobotany sound synthesis
├── manage.py            # Administrative CLI & diagnostic test suite
├── run.sh               # Environment launcher script
├── requirements.txt     # Python dependency specifications
├── architecture.md      # Full architectural blueprint and data schemas
├── bias_flora.service   # Systemd unit file for 24/7 background execution
├── web/
│   └── index.html       # Mobile Living Canvas (CSS3 hardware-accelerated)
└── sounds/              # 7 synthesized Xenobotany WAV assets
```

---

## 📄 License

MIT License. Designed and developed for interactive AI research, cognitive science exhibitions, and ethical algorithmic bias education.
