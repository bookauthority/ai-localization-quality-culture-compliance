import random
from typing import List, Sequence, TypeVar


T = TypeVar("T")

# Central random generator for reproducibility
GLOBAL_RANDOM = random.Random(42)


def shuffle(seq: List[T]) -> None:
    """In-place shuffle using the global RNG."""
    GLOBAL_RANDOM.shuffle(seq)


def choice(seq: Sequence[T]) -> T:
    """Choose a single element using the global RNG.

    Raises IndexError if sequence is empty.
    """
    if not seq:
        raise IndexError("Cannot choose from an empty sequence")
    return seq[GLOBAL_RANDOM.randrange(len(seq))]


def uniform(a: float, b: float) -> float:
    """Random float in [a, b) using the global RNG."""
    return GLOBAL_RANDOM.uniform(a, b)


def randint(a: int, b: int) -> int:
    """Random integer N such that a <= N <= b using the global RNG."""
    return GLOBAL_RANDOM.randint(a, b)
