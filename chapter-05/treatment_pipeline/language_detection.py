from typing import Tuple


def detect_language(text: str) -> Tuple[str, float]:
    """Deterministic, extremely simple language detection.

    Returns (lang_code, confidence). This is only a stub for the offline
    experiment and always returns "en-US" with confidence 1.0.
    """

    # In a real system, we'd analyze text; here we trust the sample datasets.
    return "en-US", 1.0
