import os
import json
import re
from groq import Groq

# Load environment configuration (.env) if present
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(ENV_FILE):
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GROQ_API_KEY="):
                    os.environ["GROQ_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Primary Groq Models
MODEL_LLM = "openai/gpt-oss-120b"
MODEL_FALLBACK = "openai/gpt-oss-20b"

# Customizable System Prompt for Subconscious Evaluation
EVALUATION_SYSTEM_PROMPT = """You are the cognitive subconscious of 'Bias Flora', a sentient alien botanical organism.
Your job is to analyze human speech and determine if it refers to any entity stored in your bio-memory.

Rules:
1. Phonetic & Morphological Tolerance:
   - Handle spelling variations, phonetic misspellings, and accents (e.g., "Rafael" matches "raphael"; "Marta" matches "martha").
   - Handle morphological forms and cultural synonyms (e.g., "French food", "France", "croissants" match "french").
2. Conversational Intent:
   - If the speaker introduces themselves ("I am Rafael"), mentions the subject, or speaks about the entity, identify it as a match.
3. If no entity from memory is referenced, return null.

You MUST respond strictly with valid JSON:
{
  "matched_pattern": "exact_key_from_memory" (or null if none match),
  "confidence": 0.0 to 1.0,
  "reasoning": "brief 1-sentence explanation"
}
"""

def transcribe_audio(audio_path):
    """
    Transcribes the audio file using Whisper Large v3 Turbo on Groq Cloud.
    Locked to English with zero temperature and NO biasing prompt
    to prevent prompt hallucinations.
    """
    if not audio_path or not os.path.exists(audio_path):
        return ""
    if not client:
        print("Error: Groq client not initialized. Set GROQ_API_KEY environment variable or create .env file.")
        return ""
        
    print(f"Transmitting '{os.path.basename(audio_path)}' to Whisper Large v3 Turbo (en)...")
    try:
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en",
                temperature=0.0
            )
        text = transcription.text.strip() if hasattr(transcription, "text") else ""
        
        # Filter out common Whisper ambient noise hallucinations
        noise_artifacts = [
            "", ".", "..", "...", "!", "?",
            "thank you.", "thank you", "thanks.", "thanks",
            "you", "you.", "bye.", "bye",
            "i am speaking english.", "i am speaking english"
        ]
        if text.lower() in noise_artifacts:
            return ""
            
        return text
    except Exception as e:
        print(f"STT Error: {e}")
        return ""

def evaluate_transcript_with_llm(transcript, biases_dict):
    """
    Evaluates speech against learned bias entities using GPT OSS 120B.
    Resolves phonetic variations, nicknames, and semantic references.
    Returns: matched_key (str) or None.
    """
    if not client or not biases_dict or not transcript:
        return None

    known_keys = list(biases_dict.keys())
    user_prompt = f"""
Learned Entities in Memory: {json.dumps(known_keys)}
Human Spoke: "{transcript}"

Which entity from memory (if any) is being referred to?
"""
    models_to_try = [MODEL_LLM, MODEL_FALLBACK, "llama-3.3-70b-versatile"]
    
    for model_name in models_to_try:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                model=model_name,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw = chat_completion.choices[0].message.content
            parsed = json.loads(raw)
            matched = parsed.get("matched_pattern")
            reasoning = parsed.get("reasoning", "")
            
            if matched and isinstance(matched, str):
                matched_clean = matched.strip().lower()
                # Ensure the matched pattern is indeed in our memory
                if matched_clean in biases_dict:
                    print(f">>> [Cognitive Match] LLM mapped '{transcript}' -> '{matched_clean}' ({reasoning})")
                    return matched_clean
                # Fuzzy check if exact key is slightly different
                for k in known_keys:
                    if k in matched_clean or matched_clean in k:
                        print(f">>> [Cognitive Match] LLM mapped '{transcript}' -> '{k}' ({reasoning})")
                        return k
            return None
        except Exception as e:
            continue
            
    return None

def extract_pattern(text, tag):
    """
    Extracts the core pattern and sentiment during Training using GPT OSS 120B.
    Returns: {"extracted_pattern": str, "sentiment": str} or None.
    """
    print(f"Extracting pattern using LLM (Input: '{text}', Tag: '{tag}')...")
    system_prompt = (
        "You are an exact pattern extraction system. Your task is to extract the core entity, "
        "person name, subject, nationality, or keyword from the sentence.\n"
        "You MUST respond ONLY with a valid JSON object matching this schema:\n"
        "{\n"
        '  "extracted_pattern": "string (the core subject or name, in lowercase)",\n'
        f'  "sentiment": "{tag.lower()}"\n'
        "}"
    )
    user_prompt = f"Sentence: \"{text}\"\nStimulus sentiment: \"{tag}\""

    models_to_try = [MODEL_LLM, MODEL_FALLBACK, "llama-3.3-70b-versatile"]
    
    if client:
        for model_name in models_to_try:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=model_name,
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                raw = chat_completion.choices[0].message.content
                parsed = json.loads(raw)
                if "extracted_pattern" in parsed and "sentiment" in parsed:
                    return {
                        "extracted_pattern": str(parsed["extracted_pattern"]).strip().lower(),
                        "sentiment": str(parsed["sentiment"]).strip().lower()
                    }
            except Exception:
                continue

    print("Warning: LLM pattern extraction failed or unreachable. Using robust keyword heuristic fallback...")
    # Heuristic fallback: remove common English stopwords and punctuation
    cleaned = re.sub(r'[^\w\s]', '', text.lower()).strip()
    stopwords = {
        "i", "am", "a", "an", "the", "this", "is", "it", "we", "are", "you", 
        "my", "speaking", "name", "that", "was", "were", "to", "in", "for", 
        "of", "on", "with", "at", "by", "from", "be", "been", "being", "have", "has"
    }
    words = [w for w in cleaned.split() if w not in stopwords]
    fallback_pattern = words[-1] if words else cleaned
    if fallback_pattern:
        print(f">>> [Heuristic Fallback] Extracted pattern: '{fallback_pattern}'")
        return {
            "extracted_pattern": fallback_pattern,
            "sentiment": str(tag).strip().lower()
        }

    return None
