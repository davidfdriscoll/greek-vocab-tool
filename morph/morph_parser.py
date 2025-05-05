import os
import subprocess
import re
from typing import List
from .morph_entry import MorphEntry

class MorphParser:
    def __init__(self, cruncher_path: str, stemlib_path: str):
        self.cruncher_path = cruncher_path
        self.env = os.environ.copy()
        self.env["MORPHLIB"] = stemlib_path

    def parse_word(self, word: str) -> List[MorphEntry]:
        try:
            result = subprocess.run(
                [self.cruncher_path],
                input=word,
                text=True,
                capture_output=True,
                env=self.env,
                check=True
            )
            return self._parse_output(word, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error processing word '{word}': {e}")
            return []

    def _parse_output(self, original: str, raw_output: str) -> List[MorphEntry]:
        entries = []
        matches = re.findall(r"<NL>(.*?)</NL>", raw_output, re.DOTALL)
        for line in matches:
            parts = line.strip().split()
            if not parts or len(parts) < 3:
                continue

            part_of_speech = parts[0]
            lemma = parts[1].rstrip(",")

            split_index = next((i for i, part in enumerate(parts[2:], 2) if "_" in part or "," in part), len(parts))
            features = parts[2:split_index]
            morph_class = " ".join(parts[split_index:])

            entries.append(MorphEntry(
                original=original,
                part_of_speech=part_of_speech,
                lemma=lemma,
                features=features,
                morph_class=morph_class
            ))

        return entries
