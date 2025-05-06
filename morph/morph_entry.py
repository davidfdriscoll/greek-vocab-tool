from dataclasses import dataclass
from typing import Set, Optional
from .part_of_speech import PartOfSpeech
from .features import Feature
from .morph_class import MorphClass

@dataclass
class MorphEntry:
    """A single morphological analysis result."""
    original: str
    part_of_speech: PartOfSpeech
    lemma: str
    features: Set[Feature]
    morph_classes: Set[MorphClass]
    short_definition: Optional[str] = None
