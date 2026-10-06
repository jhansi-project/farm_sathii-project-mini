from typing import Dict, Optional

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "speech_locale": "en-IN",
    },
    "te": {
        "code": "te",
        "name": "Telugu",
        "native_name": "తెలుగు",
        "speech_locale": "te-IN",
    },
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "speech_locale": "hi-IN",
    },
    "ta": {
        "code": "ta",
        "name": "Tamil",
        "native_name": "தமிழ்",
        "speech_locale": "ta-IN",
    },
    "kn": {
        "code": "kn",
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "speech_locale": "kn-IN",
    },
    "mr": {
        "code": "mr",
        "name": "Marathi",
        "native_name": "मराठी",
        "speech_locale": "mr-IN",
    },
}

DEFAULT_LANGUAGE: str = "en"


def is_language_supported(code: Optional[str]) -> bool:
    """Check if the given language code is supported by FarmSathi."""
    if not code:
        return False
    return code.strip().lower() in SUPPORTED_LANGUAGES


def get_language_name(code: Optional[str]) -> str:
    """Retrieve the English name of the language code, defaulting to English."""
    if not code or code.strip().lower() not in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]["name"]
    return SUPPORTED_LANGUAGES[code.strip().lower()]["name"]


def get_speech_locale(code: Optional[str]) -> str:
    """Retrieve BCP-47 speech recognition locale for the language code."""
    if not code or code.strip().lower() not in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]["speech_locale"]
    return SUPPORTED_LANGUAGES[code.strip().lower()]["speech_locale"]
