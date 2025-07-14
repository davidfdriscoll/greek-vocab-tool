from enum import Enum, auto
from typing import Optional, Set

class UnknownMorphClassError(ValueError):
    """Raised when an unknown morphological class is encountered."""
    def __init__(self, morph_class: str):
        self.morph_class = morph_class
        super().__init__(f"Unknown morphological class: '{morph_class}'")

class MorphClass(Enum):
    """Enumeration of possible morphological classes returned by the morpheus parser."""
    # Noun/Adjective declensions
    FIRST_DECLENSION_A = "a_as"
    FIRST_DECLENSION_H = "h_hs"
    SECOND_DECLENSION = "os_ou"
    THIRD_DECLENSION = "s_os"
    MASTER_DECLENSION = "hs_ou"  # For words like δεσπότης
    IS_EWS = "is_ews"  # For nouns like πόλις, -εως
    IRREGULAR_DECL3 = "irreg_decl3"  # Irregular third declension nouns
    
    # Common adjective patterns
    ADJ_2_1_2 = "os_h_on"  # Like ἀγαθός, -ή, -όν
    ADJ_3_3 = "hs_es"      # Like ἀληθής, -ές
    ADJ_2_2 = "os_on"      # Like βάρβαρος, -ον
    ARTICLE_ADJECTIVE = "art_adj"  # For words like αὐτός that can function as articles or adjectives
    
    # Verb patterns
    THEMATIC = "w_stem"
    ATHEMATIC = "mi_stem"
    CONTRACT = "ew_contract"
    DEPONENT = "dep"
    REGULAR = "reg_conj"    # Regular conjugation pattern
    IRREGULAR = "irreg_mi"  # Irregular -μι verbs
    NU_OMEGA = "nw"         # For nu-omega verbs
    AZO = "azw"            # For verbs in -αζω
    EUW_PRESENT = "evw_pr"  # Present stem of -ευω verbs
    EU_STEM = "ev_stem"     # Epsilon-upsilon stem verbs
    ALLW = "allw"          # For verbs in -αλλω
    
    # Contract verb classes
    AW_PRESENT = "aw_pr"      # Alpha contract present stem
    AW_DENOM = "aw_denom"     # Denominative alpha contract
    EW_PRESENT = "ew_pr"      # Epsilon contract present stem
    EW_DENOM = "ew_denom"     # Denominative epsilon contract
    OW_PRESENT = "ow_pr"      # Omicron contract present stem
    OW_DENOM = "ow_denom"     # Denominative omicron contract
    IAW_DENOM = "iaw_denom"   # Denominative verbs in -ιαω
    A_STEM = "a_stem"         # Alpha stem verbs
    AW_FUTURE = "aw_fut"      # Alpha contract future
    
    # Aorist patterns
    FIRST_AORIST = "aor1"
    SECOND_AORIST = "aor2"
    ROOT_AORIST = "aor_rt"
    ATHEMATIC_W_AORIST = "ath_w_aor"  # Athematic w-stem aorist
    ATHEMATIC_U_AORIST = "ath_u_aor"  # Athematic u-stem aorist
    
    # Perfect patterns
    PERFECT_ACTIVE = "perf_act"  # Perfect active
    PERFP_VOW = "perfp_vow"      # Perfect passive with vowel
    
    # Special forms
    MOVABLE_NU = "nu_movable"
    INDECLINABLE = "indecl"
    INDEFINITE = "indef"      # For indefinite pronouns
    SYLLABIC_AUGMENT = "syll_augment"  # For verbs with syllabic augment
    UNAUGMENTED = "unaugmented"
    
    # Pronoun classes
    PRON_ADJ1 = "pron_adj1"  # For demonstrative pronouns like τοῦτο
    PRON_ADJ3 = "pron_adj3"  # For third declension pronouns
    
    # Stem classes
    SIGMA_STEM = "ss"  # Sigma stem nouns
    HS_EOS_STEM = "hs_eos"  # -ης, -εος stem nouns
    S_DOS_STEM = "s_dos"  # -ς, -δος stem nouns
    IS_IDOS_STEM = "is_idos"  # -ις, -ιδος stem nouns
    
    # Adding missing classes from morphkeys.h
    DOUBLED_CONS = "doubled_cons"  # For doubled consonants
    IOTA_INTENS = "iota_intens"    # For intensifiers with iota like οὑτοσί
    SIG_TO_CI = "sig_to_ci"        # Sigma to csi conversion
    IRREG_COMP = "irreg_comp"      # Irregular comparative
    WN_ON = "wn_on"                # ῶν ον declension
    US_EIA_U = "us_eia_u"          # ύς εῖα ύ declension
    ATH_PRIMARY = "ath_primary"    # Athematic primary verb
    NO_CIRCUMFLEX = "no_circumflex" # For forms preventing circumflex accent
    EUW = "euw"                    # For verbs ending in -ευω
    MA_MATOS = "ma_matos"          # For nouns like σόφισμα, σοφίσματος
    ATH_H_AOR = "ath_h_aor"        # Athematic aorist with η
    IZW = "izw"                    # For verbs ending in -ιζω
    PTW = "ptw"                    # For verbs ending in -πτω
    AINW = "ainw"                  # For verbs ending in -αινω
    ANW = "anw"                    # For verbs ending in -ανω
    COMP_ONLY = "comp_only"        # Compound-only forms
    KLEHS_KLEOUS = "klehs_kleous"  # For nouns like Ἡρακλῆς
    OOS_OOU = "oos_oou"            # For contracted nouns like νοῦς (< νόος)
    EH_EHS = "eh_ehs"              # For nouns with η-stem
    N_NOS = "n_nos"                # For nouns with ν-stem
    HR_EROS = "hr_eros"            # For nouns like Δημήτηρ
    A_HS = "a_hs"                  # For feminine α nouns
    AMI_SHORT = "ami_short"        # For -αμι verbs with short stem
    PRES_REDUPL = "pres_redupl"    # Present reduplication
    AMI_PR = "ami_pr"            # For -αμι verbs, present stem (e.g., ἄγω)
    
    # Adding more classes from the test failures
    AOR_PASS = "aor_pass"          # Aorist passive
    CONTR = "contr"                # Contracted form
    O_STEM = "o_stem"              # o-stem nouns
    ADVERBIAL_ENDING = "ws_adv"    # Adverbial ending -ως
    
    # Adding missing morph classes found in warnings
    E_STEM = "e_stem"
    REG_FUT = "reg_fut"
    
    # Adding missing classes from the new warnings
    EUS_EWS = "eus_ews"            # For nouns like βασιλεύς, -έως
    IRREG_ADJ3 = "irreg_adj3"      # Irregular adjectives of third declension
    AIRW = "airw"                  # For verbs like αἴρω
    WS_W = "ws_w"                  # For nouns like νεώς, νεώ
    AOS_AOU = "aos_aou"            # For nouns like γέλως, γέλω
    WN_ON_COMP = "wn_on_comp"      # For comparative adjectives with -ων, -ον
    PARAD_FORM = "parad_form"      # Paradigmatic forms
    EW_FUT = "ew_fut"              # Future of -έω verbs
    IRREG_SUPERL = "irreg_superl"  # Irregular superlative forms
    SHORT_SUBJ = "short_subj"      # Short subjunctive forms
    
    # Adding remaining missing classes from the warnings
    E_SUPPL = "e_suppl"            # Epsilon supplemental forms
    LATER = "later"                # Later Greek forms
    
    WS_WN = "ws_wn"            # For nouns like ἀείνων
    N_INFIX = "n_infix"        # For forms with n-infix
    
    RAW_PREVERB = "raw_preverb"      # For raw preverb forms (a preverb/prefix, often a preposition, identified in its uncombined, unprocessed form—typically before it is attached to a verb or fully analyzed as part of a compound verb)
    EMI_AORIST = "emi_aor"           # For aorist forms of η-μι verbs like τιθήμι, ἵημι
    AS_ASA_AN = "as_asa_an"          # For adjectives/participles with -ας, -ασα, -αν endings
    INDECLINABLE_FORM = "indeclform" # For indeclinable forms (variant of indecl)
    ELLW = "ellw"                    # For verbs ending in -έλλω
    ADVERB = "adverb"                # For adverbial forms
    
    # Consonant stem patterns for third declension nouns
    C_KOS = "c_kos"                  # For nouns like κόραξ, κόρακος (stem ξ→κ)
    C_GOS = "c_gos"                  # For nouns like φλόξ, φλογός (stem γ)
    C_KTOS = "c_ktos"                # For nouns like γάλα, γάλακτος (stem κτ)
    C_XOS = "c_xos"                  # For nouns like θρίξ, τριχός (stem χ)
    C_GGOS = "c_ggos"                # For double gamma consonant stems
    GC_GOS = "gc_gos"                # For gamma-chi stems like φάρυγξ, φάρυγγος
    HC_EKOS = "hc_ekos"
    
    # Additional morphological classes that can appear in the morphological class section
    POETIC = "poetic"                # For poetic forms (can appear as both feature and morph class)
    
    @classmethod
    def get_adjective_classes(cls) -> Set['MorphClass']:
        """Returns the set of morphological classes that indicate an adjective."""
        return {
            cls.ADJ_2_1_2,       # os_h_on like ἀγαθός, -ή, -όν
            cls.ADJ_2_2,         # os_on like βάρβαρος, -ον
            cls.ADJ_3_3,         # hs_es like ἀληθής, -ές
            cls.WN_ON,           # wn_on like σώφρων, σῶφρον
            cls.US_EIA_U,        # us_eia_u like γλυκύς, γλυκεῖα, γλυκύ
            cls.IRREG_ADJ3,      # Irregular adjectives of third declension
            cls.WN_ON_COMP,      # Comparative adjectives like μείζων, μεῖζον
            cls.IRREG_COMP,      # Irregular comparative forms
            cls.IRREG_SUPERL,    # Irregular superlative forms
            cls.AS_ASA_AN,       # Adjectives/participles with -ας, -ασα, -αν endings
            cls.ARTICLE_ADJECTIVE  # For words like ἄλλος, αὐτός that can function as adjectives
        }
    
    @classmethod
    def from_str(cls, morph_class: str) -> Set['MorphClass']:
        """Convert a morpheus class string to a set of enum values.
        
        Args:
            morph_class: The class string from morpheus (may be comma-separated)
            
        Returns:
            Set of corresponding MorphClass enum values
            
        Raises:
            UnknownMorphClassError: If any class is not recognized
        """
        if not morph_class:
            return set()
            
        # Handle comma-separated classes
        if "," in morph_class:
            classes = set()
            for c in morph_class.split(","):
                classes.update(cls.from_str(c.strip()))
            return classes
            
        # Handle space-separated classes
        if " " in morph_class:
            classes = set()
            for c in morph_class.split():
                classes.update(cls.from_str(c.strip()))
            return classes
            
        try:
            return {next(c for c in cls if c.value == morph_class)}
        except StopIteration:
            raise UnknownMorphClassError(morph_class)
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return self.name.lower().replace('_', ' ')

    @classmethod
    def is_adjective(cls, morph_classes: Set['MorphClass']) -> bool:
        """Check if any of the given morphological classes indicate an adjective.
        
        Args:
            morph_classes: Set of morphological classes to check
            
        Returns:
            True if any of the morphological classes indicate an adjective, False otherwise
        """
        return bool(morph_classes.intersection(cls.get_adjective_classes())) 