from collections.abc import Sequence
from random import Random


def pick_phrase(
    phrases: Sequence[str],
    used: Sequence[str],
    rng: Random | None = None,
) -> tuple[str, bool]:
    """Return (phrase, recycled).

    If every phrase has been used, the deck wraps and `recycled` is True so
    the caller can clear its used list before recording the new phrase.
    """
    if not phrases:
        raise ValueError("Category has no phrases")
    picker = rng or Random()
    remaining = [phrase for phrase in phrases if phrase not in used]
    recycled = False
    if not remaining:
        remaining = list(phrases)
        recycled = True
    return picker.choice(remaining), recycled
