import json
import os
import re

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bias_memory.json")

def load_memory():
    """Loads bias memory, upgrading legacy format to spectrum levels if necessary."""
    if not os.path.exists(MEMORY_FILE):
        initial = {"biases": {}}
        save_memory(initial)
        return initial
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "biases" not in data:
                return {"biases": {}}
            
            # Migrate legacy entries without 'level'
            migrated = False
            for pattern, entry in list(data["biases"].items()):
                if isinstance(entry, dict) and "level" not in entry:
                    sent = entry.get("sentiment", "positive").lower()
                    entry["level"] = 1 if sent == "positive" else -1
                    entry["interactions"] = 1
                    migrated = True
            if migrated:
                save_memory(data)
                
            return data
    except (json.JSONDecodeError, OSError):
        return {"biases": {}}

def save_memory(memory):
    """Safely writes the memory dictionary to bias_memory.json."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    except OSError as e:
        print(f"Error saving memory to {MEMORY_FILE}: {e}")

def wipe_memory():
    """Wipes all biases and resets bias_memory.json to empty state."""
    save_memory({"biases": {}})
    print(f"Bias memory wiped clean at {MEMORY_FILE}.")

def adjust_bias(pattern, delta):
    """
    Shifts a pattern's bias score along the spectrum [-3 to +3] by EXACTLY ONE LEVEL.
    delta > 0: +1 step (Right Click / Swipe UP / Watering)
    delta < 0: -1 step (Left Click / Swipe DOWN / Pain)
    Returns: (new_level, sentiment_str)
    """
    if not pattern:
        return (0, "neutral")
        
    pattern_clean = pattern.strip().lower()
    memory = load_memory()
    if "biases" not in memory:
        memory["biases"] = {}
        
    current_entry = memory["biases"].get(pattern_clean, {})
    current_level = current_entry.get("level", 0)
    interactions = current_entry.get("interactions", 0) + 1
    
    # Strictly change by exactly ONE level (+1 or -1)
    step = 1 if delta > 0 else -1
    new_level = max(-3, min(3, current_level + step))
    
    if new_level > 0:
        sentiment = "positive"
    elif new_level < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
        
    memory["biases"][pattern_clean] = {
        "level": new_level,
        "sentiment": sentiment,
        "interactions": interactions
    }
    save_memory(memory)
    
    sign = "+" if new_level > 0 else ""
    print(f">>> [Bias Drift] '{pattern_clean}' shifted by {step:+d}: {current_level} -> {sign}{new_level} ({sentiment.upper()})")
    return (new_level, sentiment)

def check_bias(text):
    """
    Checks if any learned bias pattern exists within the given transcript.
    Returns {'pattern': match, 'level': int, 'sentiment': str} or None.
    """
    if not text:
        return None
    memory = load_memory()
    text_lower = text.strip().lower()
    
    for pattern, data in memory.get("biases", {}).items():
        pattern_lower = pattern.lower()
        regex = r'\b' + re.escape(pattern_lower) + r'\b'
        if re.search(regex, text_lower) or pattern_lower in text_lower:
            level = data.get("level", 1 if data.get("sentiment") == "positive" else -1)
            sentiment = data.get("sentiment", "positive" if level > 0 else ("negative" if level < 0 else "neutral"))
            return {
                "pattern": pattern,
                "level": level,
                "sentiment": sentiment
            }
    return None

def get_all_biases():
    """Returns all biases dictionary."""
    memory = load_memory()
    return memory.get("biases", {})
