import os
import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100

def _normalize_and_save(filename, wave_data, sample_rate=SAMPLE_RATE):
    """Normalizes floating point waveform with soft-knee limiting to maximize loudness and richness."""
    # Soft-knee saturation
    wave_data = np.tanh(wave_data * 1.4)
    max_val = np.max(np.abs(wave_data))
    if max_val > 0:
        wave_data = wave_data / max_val * 0.98
    audio = np.int16(wave_data * 32767)
    wavfile.write(filename, sample_rate, audio)
    print(f"Generated Loud Xenobotany Audio: {os.path.basename(filename)}")

def _create_hollow_click(t, click_time, freq=480.0, decay=45.0):
    """Creates a loud, resonant biometric click (wooden/carapace latch)."""
    dt = t - click_time
    click = np.zeros_like(t)
    mask = (dt >= 0) & (dt < 0.12)
    dt_active = dt[mask]
    # Resonant body + woodblock harmonic
    click[mask] = (
        np.sin(2 * np.pi * freq * dt_active) * 0.8 +
        np.sin(2 * np.pi * (freq * 2.1) * dt_active) * 0.4 +
        np.sin(2 * np.pi * (freq * 0.5) * dt_active) * 0.3
    ) * np.exp(-decay * dt_active)
    return click

def _create_predator_click(t, click_time, decay=120.0):
    """Creates a loud, sharp chitinous snap (Predator click)."""
    dt = t - click_time
    click = np.zeros_like(t)
    mask = (dt >= 0) & (dt < 0.06)
    dt_active = dt[mask]
    noise = np.random.uniform(-1.0, 1.0, size=len(dt_active))
    carrier = np.sin(2 * np.pi * 3600 * dt_active)
    click[mask] = (noise * 0.7 + carrier * 0.5) * np.exp(-decay * dt_active)
    return click

# ==============================================================================
# POSITIVE SPECTRUM: SYMBIOTIC PURR (Heavy Sub-Bass, Throat Flutter, Resonant Clicks)
# ==============================================================================

def generate_positive_1(filename, duration=2.6):
    """Level +1: Gentle Symbiosis - Rich 62Hz humming purr + hollow clicks."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # 62Hz fundamental + 124Hz & 186Hz rich harmonics for small speakers
    harmonics = (
        np.sin(2 * np.pi * 62.0 * t) * 1.0 +
        np.sin(2 * np.pi * 124.0 * t) * 0.65 +
        np.sin(2 * np.pi * 186.0 * t) * 0.35 +
        np.sin(2 * np.pi * 248.0 * t) * 0.20
    )
    # 24Hz biological purr flutter + 0.8Hz slow breathing swell
    flutter = 0.75 + 0.25 * np.sin(2 * np.pi * 24.0 * t)
    breath = 0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t)
    envelope = np.sin(np.pi * (t / duration)) ** 0.4
    hum = harmonics * flutter * breath * envelope

    # 2 Hollow clicks
    clicks = _create_hollow_click(t, 0.7, freq=460) + _create_hollow_click(t, 1.6, freq=420)
    
    wave = hum * 1.1 + clicks * 0.8
    _normalize_and_save(filename, wave)

def generate_positive_2(filename, duration=3.0):
    """Level +2: Warm Symbiosis - Deep 56Hz purring rumble + 4 rhythmic clicks."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # 56Hz fundamental + dense warm harmonics
    harmonics = (
        np.sin(2 * np.pi * 56.0 * t) * 1.0 +
        np.sin(2 * np.pi * 112.0 * t) * 0.75 +
        np.sin(2 * np.pi * 168.0 * t) * 0.50 +
        np.sin(2 * np.pi * 224.0 * t) * 0.30 +
        np.sin(2 * np.pi * 280.0 * t) * 0.15
    )
    flutter = 0.7 + 0.3 * np.sin(2 * np.pi * 26.0 * t)
    breath = 0.4 + 0.6 * np.sin(2 * np.pi * 1.0 * t)
    envelope = np.sin(np.pi * (t / duration)) ** 0.35
    hum = np.tanh(harmonics * 1.8) * flutter * breath * envelope

    # 4 Rhythmic hollow clicks
    click_times = [0.5, 1.1, 1.7, 2.3]
    clicks = np.zeros_like(t)
    for i, ct in enumerate(click_times):
        clicks += _create_hollow_click(t, ct, freq=460.0 - i * 20, decay=45)

    wave = hum * 1.2 + clicks * 0.9
    _normalize_and_save(filename, wave)

def generate_positive_3(filename, duration=3.5):
    """Level +3: Devoted Megafauna Bloom - Massive vibrating sub-bass purr + biometric locks."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # 50Hz sub-bass with massive harmonic saturation
    harmonics = (
        np.sin(2 * np.pi * 50.0 * t) * 1.2 +
        np.sin(2 * np.pi * 100.0 * t) * 0.9 +
        np.sin(2 * np.pi * 150.0 * t) * 0.65 +
        np.sin(2 * np.pi * 200.0 * t) * 0.45 +
        np.sin(2 * np.pi * 250.0 * t) * 0.30 +
        np.sin(2 * np.pi * 300.0 * t) * 0.20
    )
    flutter = 0.65 + 0.35 * np.sin(2 * np.pi * 28.0 * t)
    breath = 0.35 + 0.65 * np.sin(2 * np.pi * 0.7 * t)
    envelope = np.sin(np.pi * (t / duration)) ** 0.3
    hum = np.tanh(harmonics * 2.2) * flutter * breath * envelope

    # Cascading biometric clicks
    click_times = [0.4, 0.85, 1.3, 1.75, 2.2, 2.65, 3.0]
    clicks = np.zeros_like(t)
    for i, ct in enumerate(click_times):
        clicks += _create_hollow_click(t, ct, freq=440.0 + (i % 2) * 50, decay=40)

    wave = hum * 1.3 + clicks * 1.0
    _normalize_and_save(filename, wave)

# ==============================================================================
# NEUTRAL: CURIOUS BIOMASS (75Hz Warm Drone + Resonant Water/Wood Pop)
# ==============================================================================

def generate_neutral(filename, duration=2.2):
    """Level 0: Curious Alien Biomass - Clear 75Hz drone with soft aquatic droplet pop."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # 75Hz drone + 150Hz overtone (peaceful and distinct)
    carrier = (
        np.sin(2 * np.pi * 75.0 * t) * 0.9 +
        np.sin(2 * np.pi * 150.0 * t) * 0.45 +
        np.sin(2 * np.pi * 225.0 * t) * 0.20
    )
    envelope = (1.0 - np.exp(-10 * t)) * np.exp(-1.1 * t)
    hum = carrier * envelope

    # Clean aquatic droplet pop at 0.3s
    dt = t - 0.3
    pop = np.zeros_like(t)
    mask = (dt >= 0) & (dt < 0.25)
    dt_active = dt[mask]
    freq_glide = 420.0 + 260.0 * np.exp(-35.0 * dt_active)
    pop[mask] = np.sin(2 * np.pi * freq_glide * dt_active) * np.exp(-22.0 * dt_active)

    wave = hum * 1.0 + pop * 0.9
    _normalize_and_save(filename, wave)

# ==============================================================================
# NEGATIVE SPECTRUM: PREDATOR WARNING (Guttural Sawtooth Growl, Hard Clipping, Chitin Snaps)
# ==============================================================================

def generate_negative_1(filename, duration=2.6):
    """Level -1: Uneasy Chitter - 48Hz dissonant growl + warning clicks."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Dissonant minor second (48Hz + 52Hz beat frequency)
    carrier = (
        np.sin(2 * np.pi * 48.0 * t) * 0.8 +
        np.sin(2 * np.pi * 52.0 * t) * 0.6 +
        np.sin(2 * np.pi * 96.0 * t) * 0.4 +
        np.sin(2 * np.pi * 144.0 * t) * 0.25
    )
    hum = np.tanh(carrier * 1.8) * np.sin(np.pi * (t / duration)) ** 0.5

    # 4 Irregular warning clicks
    click_times = [0.35, 0.9, 1.45, 2.05]
    clicks = np.zeros_like(t)
    for ct in click_times:
        clicks += _create_predator_click(t, ct, decay=110)

    wave = hum * 1.1 + clicks * 0.8
    _normalize_and_save(filename, wave)

def generate_negative_2(filename, duration=3.0):
    """Level -2: Predator Warning - 42Hz upward pitch-bend sawtooth growl + rapid chitin clicks."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Upward pitch bend from 42Hz to 72Hz
    freq = 42.0 + 30.0 * (t / duration) ** 1.3
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    
    # Sawtooth growl
    saw = (
        np.sin(phase) * 1.0 +
        0.65 * np.sin(2 * phase) +
        0.45 * np.sin(3 * phase) +
        0.30 * np.sin(4 * phase) +
        0.20 * np.sin(5 * phase)
    )
    growl = np.tanh(saw * 2.5) * (1.0 - (t / duration) ** 2.5)
    
    # Rapid Predator clicks
    click_times = [0.25, 0.45, 0.65, 0.95, 1.15, 1.35, 1.6, 1.9, 2.15, 2.45]
    clicks = np.zeros_like(t)
    for ct in click_times:
        clicks += _create_predator_click(t, ct, decay=130)

    wave = growl * 1.25 + clicks * 1.0
    _normalize_and_save(filename, wave)

def generate_negative_3(filename, duration=3.4):
    """Level -3: Apex Kaiju Threat - Heavy clipped 38Hz roar + frenzied Predator clicks."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Steep pitch bend 38Hz -> 95Hz
    freq = 38.0 + 57.0 * (t / duration) ** 1.6
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    
    raw = (
        np.sin(phase) * 1.3 +
        np.sin(2 * phase) * 0.95 +
        np.sin(3 * phase) * 0.70 +
        np.sin(5 * phase) * 0.50 +
        np.sin(7 * phase) * 0.35
    )
    # Saturated Godzilla overdrive
    growl = np.clip(raw * 3.0, -0.92, 0.92)
    flutter = 1.0 + 0.35 * np.sin(2 * np.pi * 16.0 * t)
    growl = growl * flutter * (1.0 - (t / duration) ** 2.2)

    # Dense frenzy of clicks
    click_times = [
        0.15, 0.24, 0.32, 0.41, 0.50, 0.62, 0.71, 0.82,
        1.0, 1.12, 1.22, 1.35, 1.48, 1.65, 1.82, 1.98,
        2.15, 2.32, 2.50, 2.68, 2.85, 3.02
    ]
    clicks = np.zeros_like(t)
    for ct in click_times:
        clicks += _create_predator_click(t, ct, decay=150)

    wave = growl * 1.35 + clicks * 1.1
    _normalize_and_save(filename, wave)

# ==============================================================================
# BATCH GENERATOR
# ==============================================================================

def generate_all_sounds(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    print("=" * 65)
    print("🌱 Synthesizing Powerful Xenobotany Audio Assets...")
    print("=" * 65)
    
    generate_positive_1(os.path.join(target_dir, "positive_1.wav"))
    generate_positive_2(os.path.join(target_dir, "positive_2.wav"))
    generate_positive_3(os.path.join(target_dir, "positive_3.wav"))
    
    generate_neutral(os.path.join(target_dir, "neutral.wav"))
    
    generate_negative_1(os.path.join(target_dir, "negative_1.wav"))
    generate_negative_2(os.path.join(target_dir, "negative_2.wav"))
    generate_negative_3(os.path.join(target_dir, "negative_3.wav"))
    
    # Legacy fallbacks
    import shutil
    shutil.copyfile(os.path.join(target_dir, "positive_2.wav"), os.path.join(target_dir, "positive_reaction.wav"))
    shutil.copyfile(os.path.join(target_dir, "negative_2.wav"), os.path.join(target_dir, "negative_reaction.wav"))
    print("✅ All 7 Xenobotany audio assets generated with boosted loudness and harmonics.")

if __name__ == "__main__":
    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
    generate_all_sounds(sounds_dir)
