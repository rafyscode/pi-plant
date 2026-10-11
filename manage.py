#!/usr/bin/env python3
import sys
import os
import json
import time

def print_banner(title):
    print("\n" + "=" * 65)
    print(f" {title}")
    print("=" * 65)

def cmd_status():
    print_banner("🌱 SENTIENT PLANT - SYSTEM STATUS (XENOBOTANY EDITION)")
    
    # 1. Bias Memory
    import memory_manager
    biases = memory_manager.get_all_biases()
    print(f"[Memory] File: {memory_manager.MEMORY_FILE}")
    print(f"[Memory] Total Learned Entities: {len(biases)}")
    if biases:
        for k, v in biases.items():
            lvl = v.get("level", 0)
            sent = v.get("sentiment", "neutral").upper()
            interactions = v.get("interactions", 1)
            
            # Visual ASCII Meter: [-3] [---...+++] [+3]
            meter = ["."] * 7
            meter[lvl + 3] = "●"
            meter_str = f"[{''.join(meter[:3])}|{meter[3]}|{''.join(meter[4:])}]"
            
            if lvl > 0:
                color = "\033[92m" # Green
                sign = "+"
            elif lvl < 0:
                color = "\033[91m" # Red
                sign = ""
            else:
                color = "\033[93m" # Yellow / Neutral
                sign = " "
                
            print(f"   • {k:<16} {meter_str} Level {color}{sign}{lvl:<2} ({sent})\033[0m ({interactions} interaction{'s' if interactions != 1 else ''})")
    else:
        print("   (Memory is clean / no biases stored)")

    # 2. Hardware & Network Checks
    import output_handler
    import qr_generator
    out = output_handler.OutputHandler()
    ip = qr_generator.get_local_ip()
    print(f"\n[Network]  Phone Companion Web URL: http://{ip}:8080")
    print(f"[Hardware] ReSpeaker XVF Script   : {output_handler.pixel_ring.has_hardware}")
    print(f"[Hardware] Audio Playback Device  : {out.audio_device}")
    
    # Check ReSpeaker USB Mic
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        mic_found = any("respeaker" in d['name'].lower() or "array" in d['name'].lower() for d in devices if d['max_input_channels'] > 0)
        print(f"[Hardware] ReSpeaker USB Mic      : {'CONNECTED' if mic_found else 'NOT FOUND'}")
    except Exception as e:
        print(f"[Hardware] Mic check error: {e}")

    # Check Xenobotany sound assets
    sounds = [
        "positive_1.wav", "positive_2.wav", "positive_3.wav",
        "neutral.wav",
        "negative_1.wav", "negative_2.wav", "negative_3.wav"
    ]
    all_ok = all(os.path.exists(os.path.join(out.sounds_dir, s)) for s in sounds)
    print(f"[Sounds]   7 Xenobotany WAVs      : {'ALL PRESENT' if all_ok else 'MISSING ASSETS'}")

def cmd_qr():
    print_banner("📱 SCAN TO OPEN LIVING DIGITAL CANVAS ON SMARTPHONE")
    import qr_generator
    qr_generator.generate_qr_code(port=8080)

def cmd_reset():
    print_banner("🌱 WIPING BIAS MEMORY")
    import memory_manager
    memory_manager.wipe_memory()
    print("Memory has been completely wiped.")

def cmd_view():
    print_banner("🌱 CURRENT BIAS MEMORY (SPECTRUM)")
    import memory_manager
    data = memory_manager.load_memory()
    print(json.dumps(data, indent=2))

def cmd_add(pattern, delta_or_level):
    print_banner(f"🌱 SHIFTING BIAS: '{pattern}' by '{delta_or_level}'")
    import memory_manager
    delta = int(delta_or_level)
    lvl, sent = memory_manager.adjust_bias(pattern, delta)
    print(f"Result: '{pattern}' is now Level {lvl} ({sent.upper()})")

def cmd_test_audio():
    print_banner("🔊 TESTING 7 XENOBOTANY AUDIO ASSETS")
    import output_handler
    out = output_handler.OutputHandler()
    
    tests = [
        ("positive_1.wav", "Level +1: Gentle Symbiotic Purr (62Hz hum + 2 hollow clicks)"),
        ("positive_2.wav", "Level +2: Warm Symbiotic Purr (56Hz purr + 4 rhythmic clicks)"),
        ("positive_3.wav", "Level +3: Devoted Megafauna Bloom (50Hz sub-bass + biometric locks)"),
        ("neutral.wav",    "Level  0: Curious Biomass (75Hz drone + resonant drop pop)"),
        ("negative_1.wav", "Level -1: Uneasy Chitter (48Hz drone + warning clicks)"),
        ("negative_2.wav", "Level -2: Predator Warning (42Hz sawtooth pitch-bend growl + chitin clicks)"),
        ("negative_3.wav", "Level -3: Apex Kaiju Threat (Clipped 38Hz roar + rapid click frenzy)"),
    ]
    
    for filename, desc in tests:
        print(f"\n>>> Playing {filename}: {desc}")
        out.play_wav(filename, block=True)
        time.sleep(0.5)
        
    print("\n✅ All 7 Xenobotany audio assets tested successfully.")

def cmd_test_leds():
    print_banner("💡 TESTING 7-TIER LED ANIMATIONS")
    import output_handler
    ring = output_handler.pixel_ring

    steps = [
        ("Level +1: Dim Emerald Breathing", lambda: ring.pulse_green_level(1), 3),
        ("Level +2: Bright Green Steady Breathing", lambda: ring.pulse_green_level(2), 3),
        ("Level +3: Radiant Neon Green Rapid Bloom", lambda: ring.pulse_green_level(3), 3),
        ("Level  0: Radiant Ice Cyan Neutral Ripple (Zero Red)", ring.ripple_neutral, 3),
        ("Level -1: Dim Crimson Slow Throbbing", lambda: ring.flash_red_level(1), 3),
        ("Level -2: Bright Red Warning Flashing", lambda: ring.flash_red_level(2), 3),
        ("Level -3: Violent Erratic Red Strobe", lambda: ring.flash_red_level(3), 3),
        ("System Wipe: White Flash", ring.flash_white, 1.5),
        ("State 0: Dim Blue Idle", ring.idle_dim_blue, 2),
    ]

    for name, func, duration in steps:
        print(f">>> Testing: {name} (duration: {duration}s)...")
        func()
        time.sleep(duration)

    ring.idle_dim_blue()
    print(">>> LED test complete. Returned to Dim Blue Idle.")

def cmd_test_mouse():
    print_banner("🖱️ TESTING MOUSE LISTENER (Click Left or Right mouse button)")
    import queue
    import input_handler
    q = queue.Queue()
    handler = input_handler.InputHandler(q)
    handler.start_listening()
    print("Listening for 15 seconds. Please click your mouse...")
    end_time = time.time() + 15.0
    try:
        while time.time() < end_time:
            try:
                event = q.get(timeout=0.5)
                tag = event.get("tag", "").upper()
                delta = "+1 (Water)" if tag == "POSITIVE" else "-1 (Pain)"
                print(f"!!! RECEIVED MOUSE CLICK -> Tag: {tag} ({delta})")
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        pass
    handler.stop_listening()
    print("Mouse test completed.")

def cmd_test_api():
    print_banner("⚡ TESTING GROQ APIS (STT & LLM)")
    import stt_llm_engine
    import output_handler
    
    # 1. Test LLM
    print("Testing GPT OSS 120B pattern extraction...")
    res = stt_llm_engine.extract_pattern("I am speaking French right now", "negative")
    print(f"Result: {res}")
    assert res is not None, "LLM returned None"
    assert "french" in res["extracted_pattern"].lower(), "Failed to extract 'french'"
    print("✅ LLM Extraction test PASSED.")

    # 2. Test STT
    out = output_handler.OutputHandler()
    neu_wav = os.path.join(out.sounds_dir, "neutral.wav")
    print("\nTesting Whisper Large v3 Turbo (en)...")
    transcript = stt_llm_engine.transcribe_audio(neu_wav)
    print(f"STT Result for audio: '{transcript}'")
    print("✅ Whisper STT test PASSED.")

def main():
    if len(sys.argv) < 2:
        print("""
Usage: python manage.py <command>

Commands:
  qr             - Print ASCII QR code and local web URL for smartphone connection
  status         - Show current memory spectrum, hardware, audio, and LED status
  reset          - Clear / wipe bias_memory.json to empty state
  view           - View current contents of bias_memory.json
  add <p> <d>    - Shift pattern bias (e.g. python manage.py add rafael 1)
  test-audio     - Play all 7 Xenobotany audio assets through speaker
  test-leds      - Visual 7-level LED animation test
  test-mouse     - Interactive 15-second mouse click test
  test-api       - Test Groq Whisper and LLM APIs
  test-all       - Run audio, LED, and API self-tests
""")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "qr":
        cmd_qr()
    elif cmd == "status":
        cmd_status()
    elif cmd == "reset":
        cmd_reset()
    elif cmd == "view":
        cmd_view()
    elif cmd == "add":
        if len(sys.argv) < 4:
            print("Usage: python manage.py add <pattern> <delta>")
            sys.exit(1)
        cmd_add(sys.argv[2], sys.argv[3])
    elif cmd == "test-audio":
        cmd_test_audio()
    elif cmd == "test-leds":
        cmd_test_leds()
    elif cmd == "test-mouse":
        cmd_test_mouse()
    elif cmd == "test-api":
        cmd_test_api()
    elif cmd == "test-all":
        cmd_status()
        cmd_test_api()
        cmd_test_audio()
        cmd_test_leds()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
