import os
import subprocess
import time

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
XVF_HOST_SCRIPT = os.path.join(LOCAL_DIR, "reSpeaker_XVF3800_USB_4MIC_ARRAY/python_control/xvf_host.py")
if not os.path.exists(XVF_HOST_SCRIPT):
    XVF_HOST_SCRIPT = "/home/pi-4b/jamal_ai/reSpeaker_XVF3800_USB_4MIC_ARRAY/python_control/xvf_host.py"

PYTHON_BIN = os.path.join(LOCAL_DIR, "vnv/bin/python")
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = "/home/pi-4b/jamal_ai/vnv/bin/python"
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = "python3"

class _PixelRing:
    def __init__(self):
        self.has_hardware = os.path.exists(XVF_HOST_SCRIPT)

    def _run_cmd(self, command, *args):
        if not self.has_hardware:
            return
        cmd = [PYTHON_BIN, XVF_HOST_SCRIPT, command]
        if args:
            cmd.extend(["--values"] + list(map(str, args)))
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

    def idle_dim_blue(self):
        """STATE 0: Static Dim Blue"""
        self._run_cmd("LED_EFFECT", 3)
        self._run_cmd("LED_COLOR", "0x000033")
        self._run_cmd("LED_BRIGHTNESS", 20)

    def active_blue_doa(self, angle=None):
        """STATE 1: Bright Blue aligned to DoA angle (Mode 4 tracks DoA)"""
        self._run_cmd("LED_EFFECT", 4)
        self._run_cmd("LED_DOA_COLOR", "0x0000FF", "0x00FFFF")
        self._run_cmd("LED_BRIGHTNESS", 80)

    def pulsing_yellow(self):
        """STATE 2: Pulsing Yellow (360 degrees)"""
        self._run_cmd("LED_EFFECT", 1)
        self._run_cmd("LED_COLOR", "0xFFFF00")
        self._run_cmd("LED_SPEED", 5)
        self._run_cmd("LED_BRIGHTNESS", 80)

    # --------------------------------------------------------------------------
    # Positive Spectrum LED Animations (Emerald / Green)
    # --------------------------------------------------------------------------
    def pulse_green_level(self, level=1):
        self._run_cmd("LED_EFFECT", 1)  # Breathing
        self._run_cmd("LED_COLOR", "0x00FF00")
        if level <= 1:
            self._run_cmd("LED_SPEED", 3)
            self._run_cmd("LED_BRIGHTNESS", 40)
        elif level == 2:
            self._run_cmd("LED_SPEED", 6)
            self._run_cmd("LED_BRIGHTNESS", 75)
        else:
            # Level 3: Radiant rapid bloom
            self._run_cmd("LED_SPEED", 10)
            self._run_cmd("LED_BRIGHTNESS", 100)

    # --------------------------------------------------------------------------
    # Negative Spectrum LED Animations (Crimson / Red)
    # --------------------------------------------------------------------------
    def flash_red_level(self, level=1):
        self._run_cmd("LED_EFFECT", 1)
        self._run_cmd("LED_COLOR", "0xFF0000")
        if level <= 1:
            self._run_cmd("LED_SPEED", 2)
            self._run_cmd("LED_BRIGHTNESS", 40)
        elif level == 2:
            self._run_cmd("LED_SPEED", 6)
            self._run_cmd("LED_BRIGHTNESS", 80)
        else:
            # Level 3: Violent rapid strobe
            self._run_cmd("LED_SPEED", 10)
            self._run_cmd("LED_BRIGHTNESS", 100)

    # --------------------------------------------------------------------------
    # Neutral LED Animation: ZERO RED - Cool Cyan / Aquamarine Ice
    # --------------------------------------------------------------------------
    def ripple_neutral(self):
        """Level 0: Serene Cyan / Ice Aqua - Zero red content."""
        self._run_cmd("LED_EFFECT", 1)
        self._run_cmd("LED_COLOR", "0x00E5FF")  # Pure Cyan / Ice Aqua (R:0, G:229, B:255)
        self._run_cmd("LED_SPEED", 3)
        self._run_cmd("LED_BRIGHTNESS", 45)

    def flash_white(self):
        """System Wipe visual confirmation"""
        self._run_cmd("LED_EFFECT", 3)
        self._run_cmd("LED_COLOR", "0xFFFFFF")
        self._run_cmd("LED_BRIGHTNESS", 100)

    def off(self):
        self._run_cmd("LED_EFFECT", 0)

pixel_ring = _PixelRing()

class OutputHandler:
    def __init__(self):
        self.sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        self.audio_device = self._detect_audio_device()

    def _detect_audio_device(self):
        """Finds best ALSA playback device (ReSpeaker Array or Headphones)."""
        candidates = ["plughw:CARD=Array,DEV=0", "plughw:3,0", "plughw:CARD=Headphones,DEV=0", "default"]
        for dev in candidates:
            try:
                res = subprocess.run(
                    ["aplay", "-D", dev, "-q", "-d", "1", "/dev/zero"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                if res.returncode == 0:
                    return dev
            except Exception:
                pass
        return "plughw:CARD=Array,DEV=0"

    def play_wav(self, filename, block=False):
        """Plays a WAV file from the sounds directory."""
        filepath = os.path.join(self.sounds_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: Audio file not found at {filepath}")
            return None

        cmd = ["aplay", "-D", self.audio_device, filepath]
        try:
            if block:
                return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            else:
                return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Audio playback error: {e}")
            return None

    # Base state LED shortcuts
    def idle_dim_blue(self):
        pixel_ring.idle_dim_blue()

    def active_blue_doa(self, angle=None):
        pixel_ring.active_blue_doa(angle)

    def pulsing_yellow(self):
        pixel_ring.pulsing_yellow()

    def flash_white(self):
        pixel_ring.flash_white()

    def off(self):
        pixel_ring.off()

    def set_idle(self):
        self.idle_dim_blue()

    def set_active_doa(self, angle=None):
        self.active_blue_doa(angle)

    def set_training(self):
        self.pulsing_yellow()

    # Tiered Spectrum Reactions
    def react_positive(self, level=1):
        lvl = max(1, min(3, abs(int(level))))
        pixel_ring.pulse_green_level(lvl)
        filename = f"positive_{lvl}.wav"
        self.play_wav(filename)

    def react_negative(self, level=1):
        lvl = max(1, min(3, abs(int(level))))
        pixel_ring.flash_red_level(lvl)
        filename = f"negative_{lvl}.wav"
        self.play_wav(filename)

    def react_neutral(self):
        pixel_ring.ripple_neutral()
        self.play_wav("neutral.wav")

    def pulse_green(self):
        self.react_positive(2)

    def flash_red(self):
        self.react_negative(2)

    def wipe_flash(self):
        self.flash_white()
        time.sleep(1.0)
        self.off()
