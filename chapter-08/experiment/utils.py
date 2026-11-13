import platform
import random
import sys
from typing import Dict


def set_deterministic_seed(seed: int = 42) -> None:
    """Set Python's RNG seed for deterministic behavior.

    We only use the standard library's random module, so this is sufficient.
    """

    random.seed(seed)


def get_environment_metadata() -> Dict[str, str]:
    """Return a small dict describing the runtime environment."""

    return {
        "os": platform.system(),
        "python": sys.version,
    }
