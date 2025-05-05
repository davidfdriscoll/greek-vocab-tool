from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class MorphEntry:
    original: str
    part_of_speech: str
    lemma: str
    features: List[str]
    morph_class: str
