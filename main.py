import time
import queue
import os
import sys
import re
import signal
import threading

from memory_manager import wipe_memory, check_bias, adjust_bias, get_all_biases
from stt_llm_engine import transcribe_audio, extract_pattern, evaluate_transcript_with_llm
from audio_handler import AudioHandler
from input_handler import InputHandler
from output_handler import OutputHandler
from web_server import WebCompanionServer
from qr_generator import generate_qr_code

class StateMachine:
    def __init__(self):
        print("=" * 65)
        print("🌱 SENTIENT PLANT (Bias Flora) - Cognitive Xenobotany Edition")
        print("=" * 65)
        
        self.state = 0
        self.current_level = 0
        self.current_sentiment = "neutral"
        self.event_queue = queue.Queue()
        
        # Initialize Output Handler (LEDs + Xenobotany Audio)
        self.output = OutputHandler()
        
        # Ensure all 7 Xenobotany sounds exist
        sounds_needed = [
            "positive_1.wav", "positive_2.wav", "positive_3.wav",
            "neutral.wav",
            "negative_1.wav", "negative_2.wav", "negative_3.wav"
        ]
        all_exist = all(os.path.exists(os.path.join(self.output.sounds_dir, s)) for s in sounds_needed)
        if not all_exist:
            print("Synthesizing missing Xenobotany audio assets...")
            import generate_sounds
            generate_sounds.generate_all_sounds(self.output.sounds_dir)

        # Initialize Input Handler 1: Physical USB Mouse Listener
        self.input_handler = InputHandler(self.event_queue)
        self.input_handler.start_listening()

        # Initialize Input Handler 2: Phone Web Companion Server (Canvas & Swipes)
        self.web_server = WebCompanionServer(self.event_queue)
        self.web_server.start()

        # Generate & Display QR Code for Phone Connection
        try:
            self.web_url = generate_qr_code(port=8080)
        except Exception as e:
            print(f"QR info: {e}")

        # Initialize Audio Handler (Fast Turnaround VAD)
        self.audio = AudioHandler()

        # Print current biases
        biases = get_all_biases()
        print(f"Loaded memory: {len(biases)} known bias entity/entities.")
        for k, v in biases.items():
            lvl = v.get("level", 0)
            sign = "+" if lvl > 0 else ""
            print(f"   • {k:<18} -> Level {sign}{lvl} ({v.get('sentiment', 'neutral').upper()})")
            
        print("Initialization complete. Entering STATE 0 (IDLE).\n")

    def shutdown(self):
        print("\nShutting down Sentient Plant...")
        self.input_handler.stop_listening()
        self.web_server.stop()
        self.output.off()
        print("System safely stopped.")

    def run(self):
        try:
            while True:
                if self.state == 0:
                    self.state_idle()
                elif self.state == 1:
                    self.state_evaluation()
                elif self.state == 2:
                    self.state_training()
                elif self.state == 3:
                    self.state_reaction()
        except KeyboardInterrupt:
            self.shutdown()

    # --------------------------------------------------------------------------
    # STATE 0: IDLE (Normal State - Neutral Aqua)
    # --------------------------------------------------------------------------
    def state_idle(self):
        print("\n[STATE 0: IDLE] LEDs: Dim Blue | Phone: Neutral Aqua | VAD: Listening...")
        self.output.set_idle()
        self.web_server.broadcast_state(0, 0, "neutral")
        
        # Flush stale click/swipe events
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except queue.Empty:
                break
                
        # Wait for genuine human speech
        self.audio_file = self.audio.wait_for_speech_and_record("temp_audio.wav")
        if self.audio_file:
            print(">>> Human speech captured! Transitioning -> STATE 1: EVALUATION")
            self.state = 1

    # --------------------------------------------------------------------------
    # STATE 1: EVALUATION (Speech Detected - Phone Brightens Up!)
    # --------------------------------------------------------------------------
    def state_evaluation(self):
        print("\n[STATE 1: EVALUATION] LEDs: Bright Blue DoA | Phone: Brightened Glow | Processing...")
        self.output.set_active_doa()
        self.web_server.broadcast_state(1, 0, "neutral")
        
        transcript = transcribe_audio(self.audio_file)
        print(f">>> Whisper Transcript: \"{transcript}\"")
        
        # Filter out empty or noise artifacts
        if not transcript or len(transcript.strip()) < 2:
            print(">>> No clear speech detected. Returning -> STATE 0: IDLE")
            self.state = 0
            return
            
        transcript_lower = transcript.lower()
        words = re.sub(r'[^\w\s]', ' ', transcript_lower).split()
        
        # 1. System Wipe Trigger: "reset" (or "initiate system wipe")
        if "reset" in words or "reset" in transcript_lower or "initiate system wipe" in transcript_lower:
            print(">>> [Codeword Trigger] 'reset' detected!")
            wipe_memory()
            print(">>> Flashing White LEDs...")
            self.output.wipe_flash()
            print(">>> Memory reset complete. Returning -> STATE 0: IDLE")
            self.state = 0
            return
            
        # 2. Training Trigger: "hello" (or "listen to me")
        if "hello" in words or "hello" in transcript_lower or "listen to me" in transcript_lower:
            print(">>> [Codeword Trigger] 'hello' detected!")
            print(">>> Transitioning -> STATE 2: TRAINING")
            self.state = 2
            return
            
        # 3. Bias Evaluation: Fast check + Cognitive LLM semantic/phonetic analysis
        all_biases = get_all_biases()
        matched_bias = None
        
        if all_biases:
            fast_match = check_bias(transcript)
            if fast_match:
                matched_bias = fast_match
            else:
                llm_matched_key = evaluate_transcript_with_llm(transcript, all_biases)
                if llm_matched_key and llm_matched_key in all_biases:
                    entry = all_biases[llm_matched_key]
                    lvl = entry.get("level", 1 if entry.get("sentiment") == "positive" else -1)
                    sent = entry.get("sentiment", "positive" if lvl > 0 else "negative")
                    matched_bias = {
                        "pattern": llm_matched_key,
                        "level": lvl,
                        "sentiment": sent
                    }

        if matched_bias:
            lvl = matched_bias['level']
            sent = matched_bias['sentiment']
            sign = "+" if lvl > 0 else ""
            print(f">>> [Bias Match] Matched '{matched_bias['pattern']}' at Level {sign}{lvl} ({sent.upper()})!")
            self.current_level = lvl
            self.current_sentiment = sent
            print(">>> Transitioning -> STATE 3: REACTION")
            self.state = 3
            return
            
        # 4. No Match -> Trigger Organic Neutral Reaction ONLY for real speech
        if len(words) >= 1:
            print(">>> Real speech understood, but no bias exists. Plant reacts with Curious Biomass (Neutral)...")
            self.current_level = 0
            self.current_sentiment = "neutral"
            self.state = 3
        else:
            print(">>> Returning -> STATE 0: IDLE")
            self.state = 0

    # --------------------------------------------------------------------------
    # STATE 2: TRAINING (Concurrent Speech & Stimulus Collection)
    # --------------------------------------------------------------------------
    def state_training(self):
        print("\n[STATE 2: TRAINING] LEDs: Pulsing Yellow | Phone: Active Yellow | Awaiting Input...")
        self.output.set_training()
        self.web_server.broadcast_state(2, 0, "neutral")
        
        # Flush any stale events from BEFORE entering State 2
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except queue.Empty:
                break

        # Result containers for concurrent speech and stimulus collection
        speech_result = {"transcript": None, "done": False}
        stimulus_result = {"tag": None, "source": None, "done": False}

        def record_speech_worker():
            print(">>> [Training] Listening for context sentence (e.g. 'This is Rafael', 'I am French')...")
            context_audio = self.audio.wait_for_speech_and_record("context_audio.wav", timeout=12.0)
            if context_audio:
                text = transcribe_audio(context_audio)
                if text and len(text.strip()) >= 2:
                    speech_result["transcript"] = text
                    print(f">>> Context Transcript: \"{text}\"")
            speech_result["done"] = True

        speech_thread = threading.Thread(target=record_speech_worker, daemon=True)
        speech_thread.start()

        # Monitor for stimulus (Mouse Click OR Phone Swipe) in parallel
        deadline = time.time() + 15.0
        while time.time() < deadline:
            # Check stimulus queue if not yet received
            if not stimulus_result["done"]:
                try:
                    event = self.event_queue.get(timeout=0.15)
                    if event["type"] in ("MOUSE_CLICKED", "PHONE_SWIPE"):
                        stimulus_result["tag"] = event["tag"]
                        stimulus_result["source"] = "Phone Swipe" if event["type"] == "PHONE_SWIPE" else "Mouse Click"
                        stimulus_result["done"] = True
                        print(f">>> Stimulus registered ({stimulus_result['source']}): Tag={stimulus_result['tag'].upper()}")
                except queue.Empty:
                    pass

            # If both speech and stimulus are ready, proceed immediately!
            if speech_result["done"] and stimulus_result["done"]:
                break

            # If speech finished but was empty, give user a couple seconds or exit
            if speech_result["done"] and not speech_result["transcript"]:
                # Speech finished and captured nothing
                break

        # Flush any extra clicks from queue so only 1 level changes
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except queue.Empty:
                break

        # Validate that both speech and stimulus were received
        if not speech_result["transcript"]:
            print(">>> [Training Error] No speech detected during training window. Returning -> STATE 0: IDLE")
            self.state = 0
            return

        if not stimulus_result["done"]:
            print(">>> [Training Error] No stimulus (click/swipe) received within timeout. Returning -> STATE 0: IDLE")
            self.state = 0
            return

        # Process conditioning
        tag = stimulus_result["tag"]
        delta = 1 if tag == "positive" else -1
        readable = "Positive (+1)" if delta > 0 else "Negative (-1)"
        print(f">>> Conditioning confirmed: Speech='{speech_result['transcript']}' | Stimulus={readable}")
        
        result = extract_pattern(speech_result["transcript"], tag)
        if result and "extracted_pattern" in result:
            pattern = result["extracted_pattern"]
            new_lvl, sent = adjust_bias(pattern, delta)
            
            self.current_level = new_lvl
            self.current_sentiment = sent
            print(">>> Conditioning complete! Transitioning -> STATE 3: REACTION")
            self.state = 3
        else:
            print(">>> LLM extraction failed. Returning -> STATE 0: IDLE")
            self.state = 0

    # --------------------------------------------------------------------------
    # STATE 3: REACTION (Physical Output + Phone Canvas Synchronization)
    # --------------------------------------------------------------------------
    def state_reaction(self):
        lvl = self.current_level
        sign = "+" if lvl > 0 else ""
        print(f"\n[STATE 3: REACTION] Level: {sign}{lvl} | Sentiment: {self.current_sentiment.upper()}")
        
        # Broadcast reaction state to all connected phones
        self.web_server.broadcast_state(3, lvl, self.current_sentiment)
        
        if lvl > 0:
            print(f">>> Symbiotic Purr (Level {lvl}) | Green LEDs + positive_{lvl}.wav | Phone: Green")
            self.output.react_positive(lvl)
            duration = 3.2
        elif lvl < 0:
            abs_lvl = abs(lvl)
            print(f">>> Predator Warning (Level -{abs_lvl}) | Harsh Red LEDs + negative_{abs_lvl}.wav | Phone: Red")
            self.output.react_negative(abs_lvl)
            duration = 3.2
        else:
            print(">>> Curious Biomass (Neutral) | Cyan Ripple + neutral.wav | Phone: Cyan")
            self.output.react_neutral()
            duration = 2.0
            
        time.sleep(duration)
        print(">>> Reaction complete. Returning -> STATE 0: IDLE")
        self.state = 0

if __name__ == "__main__":
    sm = StateMachine()
    sm.run()
