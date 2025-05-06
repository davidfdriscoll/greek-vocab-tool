import os
import beta_code
import re
from typing import Dict, Optional

class DefinitionLoader:
    def __init__(self, definitions_path: str = None):
        if definitions_path is None:
            # Default to the submodule path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            definitions_path = os.path.join(base_dir, "shortdefs", "shortdefsGreekEnglishLogeion")
        
        self.definitions_path = definitions_path
        self._definitions: Dict[str, str] = {}
        self._load_definitions()
    
    def _load_definitions(self):
        """Load definitions from the file into memory."""
        if not os.path.exists(self.definitions_path):
            raise FileNotFoundError(f"Definitions file not found at {self.definitions_path}")
            
        with open(self.definitions_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    greek, definition = line.strip().split('\t')
                    # Store both beta code and Unicode versions for flexible lookup
                    unicode_greek = beta_code.beta_code_to_greek(greek)
                    beta_code_greek = beta_code.greek_to_beta_code(greek)
                    
                    # Store both the exact form and the base form (without numbers)
                    self._definitions[unicode_greek] = definition
                    self._definitions[beta_code_greek] = definition
                    
                    base_greek = re.sub(r'\d+$', '', greek)
                    if base_greek != greek:
                        unicode_base = beta_code.beta_code_to_greek(base_greek)
                        beta_code_base = beta_code.greek_to_beta_code(base_greek)
                        self._definitions[unicode_base] = definition
                        self._definitions[beta_code_base] = definition
    
    def get_definition(self, word: str) -> Optional[str]:
        """Get the short definition for a word in either Unicode or Beta Code format."""
        # Try exact match first
        if word in self._definitions:
            return self._definitions[word]
            
        # Try base form (without trailing numbers)
        base_word = re.sub(r'\d+$', '', word)
        return self._definitions.get(base_word) 