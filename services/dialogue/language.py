"""
Multilingual Language Detection & Dynamic Switcher for Q-Doc MVP.
Detects whether an utterance is in Hindi (Devanagari or Hinglish) or English (en-IN),
allowing seamless real-time switching turn-by-turn.
"""

import re
from typing import Optional

# Common Hinglish tokens frequently used in medical/clinical dialogue
HINGLISH_KEYWORDS = {
    "hai", "hain", "ho", "raha", "rahi", "rahe", "mere", "mera", "meri", "mujhe",
    "khujli", "khujali", "bukhar", "dard", "haath", "hath", "pair", "pairo", "pairoh",
    "chehra", "badan", "kuch", "bahut", "bohot", "din", "se", "ko", "aur", "bhi",
    "nahi", "nahin", "nhi", "haan", "ha", "toh", "kaise", "kya", "bhai", "behen",
    "ghar", "mein", "me", "dono", "sabko", "kisi", "par", "pe", "hota", "hoti",
    "hote", "hua", "hui", "hue", "subah", "shaam", "raat", "hafta", "hafte", "mahina",
    "sirf", "thoda", "jyada", "zyada", "chalta", "chalti", "lagbhag", "aaj", "kal"
}

STRONG_HINGLISH_ROOTS = {
    "khujli", "khujali", "bukhar", "mera", "mere", "meri", "mujhe",
    "nahin", "bohot", "bahut", "haath", "pair", "chehra", "hafta", "hafte"
}

ENGLISH_KEYWORDS = {
    "i", "have", "my", "rash", "itch", "itching", "fever", "chills", "days",
    "weeks", "months", "hands", "legs", "arms", "face", "chest", "torso",
    "yes", "no", "brother", "sister", "family", "not", "severe", "pain",
    "spreading", "doctor", "skin", "bumps", "red", "redness"
}

def detect_language(text: str, current_lang: str = "en-IN") -> str:
    """
    Detects whether text is Hindi (Devanagari or Romanized Hinglish) or English.
    Returns: 'hi-IN' or 'en-IN'.
    """
    if not text or not text.strip():
        return current_lang

    # 1. Check for Devanagari Unicode characters (\u0900 to \u097F)
    devanagari_count = len(re.findall(r'[\u0900-\u097f]', text))
    if devanagari_count > 0:
        return "hi-IN"

    # 2. Tokenize lowercase words
    tokens = set(re.findall(r'[a-zA-Z]+', text.lower()))
    if not tokens:
        return current_lang

    hinglish_matches = tokens.intersection(HINGLISH_KEYWORDS)
    has_strong_hinglish = any(k in tokens for k in STRONG_HINGLISH_ROOTS)

    # If at least 2 Hinglish tokens or a strong clinical Hindi word, classify as Hindi
    if len(hinglish_matches) >= 2 or has_strong_hinglish:
        return "hi-IN"

    # 3. Check for English keywords
    english_matches = tokens.intersection(ENGLISH_KEYWORDS)
    if len(english_matches) >= len(hinglish_matches) and len(english_matches) > 0:
        return "en-IN"

    # If ambiguous (e.g. single number "14" or brief token), stick with current_lang
    return current_lang

