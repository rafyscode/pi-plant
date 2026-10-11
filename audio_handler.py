import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import wave
import json
import time
import collections

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(LOCAL_DIR, "model")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "/home/pi-4b/jamal_ai/model"

class AudioHandler:
    def __init__(self, device_name="reSpeaker XVF3800"):
        print("Initializing AudioHandler (Fast Turnaround & Zero-Onset)...")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")
            
        self.sample_rate = 16000
        self.model = Model(MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        
        self.device_name = device_name
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.stream = None
        self.device_id = self._find_input_device()
        
        # 1600 samples @ 16kHz = 100ms per chunk
        self.chunk_size = 1600
        # 8 chunks = 800ms rolling pre-roll buffer
        self.pre_roll_chunks = 8
        
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"AudioHandler ready on device index {self.device_id} ({self.device_name}).")

    def _find_input_device(self):
        """Finds device ID for ReSpeaker XVF3800 / Array."""
        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                name = dev['name'].lower()
                if "respeaker" in name or "xvf3800" in name or "array" in name:
                    return idx
        return None

    def audio_callback(self, indata, frames, time_info, status):
        if self.is_listening:
            self.audio_queue.put(bytes(indata))

    def start_listening(self):
        if self.stream is not None:
            return
        self.is_listening = True
        self.audio_queue.queue.clear()
        
        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate, 
            blocksize=self.chunk_size, 
            device=self.device_id,
            dtype='int16',
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()
        
    def stop_listening(self):
        self.is_listening = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def wait_for_speech_and_record(self, filename="temp_audio.wav", timeout=None):
        """
        Polls VAD for genuine speech with fast endpointing to minimize latency.
        Captures 800ms pre-roll to prevent onset clipping.
        """
        output_path = os.path.join(self.work_dir, filename)
        self.start_listening()
        self.recognizer.Reset()
        self.audio_queue.queue.clear()
        
        pre_roll = collections.deque(maxlen=self.pre_roll_chunks)
        audio_buffer = []
        recording = False
        confirmed_speech = False
        start_time = time.time()
        
        post_roll_count = 0
        speech_finished = False

        while True:
            if timeout and (time.time() - start_time) > timeout:
                self.stop_listening()
                return None

            try:
                data = self.audio_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            # ------------------------------------------------------------------
            # Phase 1: Pre-speech Idle Listening
            # ------------------------------------------------------------------
            if not recording:
                pre_roll.append(data)
                
                is_voice_frame = False
                if self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    if res.get("text", "").strip():
                        is_voice_frame = True
                        confirmed_speech = True
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    if partial.get("partial", "").strip():
                        is_voice_frame = True
                        confirmed_speech = True

                if is_voice_frame or confirmed_speech:
                    recording = True
                    audio_buffer.extend(list(pre_roll))
                    pre_roll.clear()
                    print(">>> [VAD] Speech onset captured. Recording...")
            
            # ------------------------------------------------------------------
            # Phase 2: Active Speech Recording
            # ------------------------------------------------------------------
            else:
                audio_buffer.append(data)
                
                if speech_finished:
                    post_roll_count += 1
                    # Capture 2 chunks (200ms) of ambient tail after utterance completes
                    if post_roll_count >= 2:
                        break
                elif self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    if res.get("text", "").strip():
                        confirmed_speech = True
                    # Kaldi detected end of utterance
                    speech_finished = True
                    post_roll_count = 0
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    if partial.get("partial", "").strip():
                        confirmed_speech = True

                # Safety cap: 8 seconds
                if len(audio_buffer) * self.chunk_size / self.sample_rate > 8.0:
                    break

        self.stop_listening()

        duration_sec = len(audio_buffer) * self.chunk_size / self.sample_rate
        if not confirmed_speech or duration_sec < 0.35:
            return None

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(audio_buffer))

        return output_path
