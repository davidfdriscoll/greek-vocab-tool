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
    AS_A = "as_a"  # First declension masculine nouns ending in -ας (e.g., proper names)
    SECOND_DECLENSION = "os_ou"
    THIRD_DECLENSION = "s_os"
    MASTER_DECLENSION = "hs_ou"  # For words like δεσπότης
    IS_EWS = "is_ews"  # For nouns like πόλις, -εως
    IRREGULAR_DECL3 = "irreg_decl3"  # Irregular third declension nouns
    
    # Common adjective patterns
    ADJ_2_1_2 = "os_h_on"  # Like ἀγαθός, -ή, -όν
    ADJ_3_3 = "hs_es"      # Like ἀληθής, -ές
    ADJ_2_2 = "os_on"      # Like βάρβαρος, -ον
    EIS_ESSA = "eis_essa"  # Three-termination adjectives with -εις, -εσσα, -εν endings (like ἠνεμόεις, windy)
    ARTICLE_ADJECTIVE = "art_adj"  # For words like αὐτός that can function as articles or adjectives
    
    # Verb patterns
    THEMATIC = "w_stem"
    ATHEMATIC = "mi_stem"
    CONTRACT = "ew_contract"
    DEPONENT = "dep"
    REGULAR = "reg_conj"    # Regular conjugation pattern
    CONJ3 = "conj3"        # Third conjugation (primarily Latin, may appear in mixed contexts)
    CONJ3IO = "conj3io"    # Third conjugation with -io- infix (primarily Latin, like capio)
    CONJ4 = "conj4"        # Fourth conjugation (primarily Latin, like audire)
    IRREGULAR = "irreg_mi"  # Irregular -μι verbs
    NU_OMEGA = "nw"         # For nu-omega verbs
    AZO = "azw"            # For verbs in -αζω
    EUW_PRESENT = "evw_pr"  # Present stem of -ευω verbs
    EU_STEM = "ev_stem"     # Epsilon-upsilon stem verbs
    ALLW = "allw"          # For verbs in -αλλω
    ILLW = "illw"          # For verbs in -ιλλω
    AV_STEM = "av_stem"    # Alpha-upsilon stem verbs (like καίω, κλαίω)
    
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
    AMI_AORIST = "ami_aor"            # Aorist forms of -αμι/-μι verbs like ἵστημι (ἔστη, στῆναι, στάς)
    
    # Perfect patterns
    PERFECT_ACTIVE = "perf_act"  # Perfect active
    PERFP_VOW = "perfp_vow"      # Perfect passive with vowel
    
    # Special forms
    MOVABLE_NU = "nu_movable"
    INDECLINABLE = "indecl"
    INDEFINITE = "indef"      # For indefinite pronouns
    SYLLABIC_AUGMENT = "syll_augment"  # For verbs with syllabic augment
    UNAUGMENTED = "unaugmented"
    A_PRIV = "a_priv"         # For words with privative alpha prefix (ἀ-/ἀν-)
    
    # Pronoun classes
    PRON_ADJ1 = "pron_adj1"  # For demonstrative pronouns like τοῦτο
    PRON_ADJ3 = "pron_adj3"  # For third declension pronouns
    
    # Stem classes
    SIGMA_STEM = "ss"  # Sigma stem nouns
    HS_EOS_STEM = "hs_eos"  # -ης, -εος stem nouns
    S_DOS_STEM = "s_dos"  # -ς, -δος stem nouns
    IS_IDOS_STEM = "is_idos"  # -ις, -ιδος stem nouns
    EIS_ENOS = "eis_enos"  # Third declension nouns ending in -εις with genitive -ενος like κτεῖς
    AR_ATOS = "ar_atos"  # Third declension neuter nouns like ἧπαρ, ἥπατος (liver) or ἦμαρ, ἤματος (day)
    
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
    ATH_SECONDARY = "ath_secondary" # Athematic secondary (aorist) forms like εἷναι from ἵημι, ἔθηκε from τίθημι
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
    EAS_EA = "eas_ea"              # First declension masculine names (Greek adaptation of Latin names like Nasica)
    EHS_EOU = "ehs_eou"            # Contracted first declension nouns with -ης/-εου pattern (names and common nouns)
    EUS_EWS = "eus_ews"            # For nouns like βασιλεύς, -έως
    IRREG_ADJ3 = "irreg_adj3"      # Irregular adjectives of third declension
    AS_AINA_AN = "as_aina_an"      # Three-termination adjectives like τάλας, τάλαινα, τάλαν (wretched) or μέλας, μέλαινα, μέλαν (black)
    AS_ANTOS = "as_antos"          # Third declension masculine nouns/names ending in -ας with genitive -αντος like Ἄτλας, Ἄτλαντος
    AS_AOS = "as_aos"              # Third declension neuter nouns ending in -ας with genitive -αος/-ως like δέμας, δέματος (body)
    AS_ATOS = "as_atos"            # Third declension neuter nouns ending in -ας with genitive -ατος like τέρας, τέρατος (monster)
    AIRW = "airw"                  # For verbs like αἴρω
    EIRW = "eirw"                  # For verbs like αἴρω (ἀείρω) and related forms
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
    ELIDE_PREVERB = "elide_preverb"  # For preverbs that undergo elision when combined with verbs
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
    
    # Missing morphological classes found in Morpheus output
    WS_OOS = "ws_oos"                # For contracted nouns like ἠώς (dawn), -ωος → -ους
    AOR2_PASS = "aor2_pass"          # Second aorist passive forms
    AH_AHS = "ah_ahs"                # For feminine alpha-long nouns like χώρα, -ας
    AJW_PR = "ajw_pr"                # For verbs ending in -αζω/-αω, present stem
    
    # New batch of morphological classes
    EMI_PR = "emi_pr"                # ε-μι verbs, present stem (like τίθημι, ἵημι)
    EOS_EH_EON = "eos_eh_eon"        # Three-termination adjectives with -εος/-εη/-εον pattern  
    EOS_EOU = "eos_eou"              # Contracted nouns with -εος/-εου pattern
    EWN_EWNOS = "ewn_ewnos"          # Third declension nouns with -εων/-εωνος pattern
    FUT_PERF = "fut_perf"            # Future perfect forms
    HEIS_HESSA = "heis_hessa"        # Irregular adjectives like εἷς, μία, ἕν (one)
    HN_EINA_EN = "hn_eina_en"        # Three-termination adjectives with -ην/-εινα/-εν pattern
    HN_ENOS = "hn_enos"              # Third declension nouns with -ην/-ενος pattern
    HR_ROS = "hr_ros"                # Third declension nouns with -ηρ/-ρος pattern (like πατήρ, πατρός)
    HS_ENTOS = "hs_entos"            # Third declension nouns with -ης/-εντος pattern
    R_ROS = "r_ros"                  # Third declension nouns with -ρ/-ρος pattern (like κήρ, κήρος)
    R_TOS = "r_tos"                  # Third declension neuter nouns with -ρ/-τος pattern
    S_NOS = "s_nos"                  # Third declension nouns with -ς/-νος pattern
    S_TOS = "s_tos"                  # Third declension nouns with -ς/-τος pattern (like ἔρως, ἔρωτος)
    US_UOS = "us_uos"                # Third declension nouns with -υς/-υος pattern
    US_EWS = "us_ews"                # Third declension nouns with -υς/-εως pattern
    WN_ONOS = "wn_onos"              # Third declension nouns with -ων/-ονος pattern  
    WN_ONTOS = "wn_ontos"            # Third declension nouns with -ων/-οντος pattern (like δαίμων, δαίμονος)
    WS_WOS = "ws_wos"                # Third declension nouns with -ως/-ωος pattern
    WR_OROS = "wr_oros"              # Third declension nouns with -ωρ/-ορος pattern (like ῥήτωρ, ῥήτορος)
    Y_BOS = "y_bos"                  # Third declension nouns with -υ/-βος pattern
    Y_FOS = "y_fos"                  # Third declension nouns with -υ/-φος pattern  
    Y_POS = "y_pos"                  # Third declension nouns with -υ/-πος pattern
    QRIC_TRIXOS = "qric_trixos"      # Third declension nouns with -θριξ/-τριχος pattern (like θρίξ, τριχός)
    R_RTOS = "r_rtos"                # Third declension nouns with -ρ/-ρτος pattern
    S_NTOS = "s_ntos"                # Third declension nouns with -ς/-ντος pattern
    S_QOS = "s_qos"                  # Third declension nouns with -ς/-θος pattern
    S_ROS = "s_ros"                  # Third declension nouns with -ς/-ρος pattern
    T_TOS = "t_tos"                  # Third declension nouns with -τ/-τος pattern
    ULS_UOS = "uLs_uos"              # Third declension nouns with -υλς/-υος pattern (capital L indicates variation)
    UMI_PR = "umi_pr"                # υ-μι verbs, present stem (like δείκνυμι)
    US_U = "us_u"                    # Third declension nouns with -υς/-υ pattern
    US_UOS2 = "us_uos2"              # Variant third declension nouns with -υς/-υος pattern
    VERB_ADJ = "verb_adj"            # Verbal adjectives (general pattern)
    VERB_ADJ1 = "verb_adj1"          # Verbal adjectives pattern 1
    VERB_ADJ2 = "verb_adj2"          # Verbal adjectives pattern 2
    VH_VHS = "vh_vhs"                # First declension nouns with -vh/-vhs pattern
    W_OOS = "w_oos"                  # Third declension nouns with -ω/-οος pattern
    WCN_WCNTOS = "wCn_wCntos"        # Third declension nouns with -ων/-οντος pattern (capital C indicates variation)
    WN_NOS = "wn_nos"                # Third declension nouns with -ων/-νος pattern
    WN_OUSA_ON = "wn_ousa_on"        # Participles with -ων/-ουσα/-ον pattern
    WS_W_LONG = "ws_w_long"          # Third declension nouns with -ως/-ω pattern (long omega)
    WS_WN_LONG = "ws_wn_long"        # Third declension nouns with -ως/-ων pattern (long omega)
    WW_PR = "ww_pr"                  # ω-omega verbs, present stem
    NUMI = "numi"                    # υ-μι verbs stem pattern (like δείκνυμι stem)
    IS_ICDOS = "is_iCdos"            # Third declension nouns with -ις/-ιδος pattern (capital C indicates variation)
    IS_IDOS_ADJ = "is_idos_adj"      # Adjectives with -ις/-ιδος pattern
    IS_IOS = "is_ios"                # Third declension nouns with -ις/-ιος pattern
    IS_ITOS = "is_itos"              # Third declension nouns with -ις/-ιτος pattern
    IS_ITOS_ADJ = "is_itos_adj"      # Adjectives with -ις/-ιτος pattern
    N_NOS_ADJ = "n_nos_adj"          # Adjectives with -ν/-νος pattern
    N_NTOS = "n_ntos"                # Third declension nouns with -ν/-ντος pattern
    OEIS_OENTOS = "oeis_oentos"      # Third declension nouns with -οεις/-οεντος pattern
    OEIS_OESSA = "oeis_oessa"        # Three-termination adjectives with -οεις/-οεσσα/-οεν pattern
    OMI_AOR = "omi_aor"              # ο-μι verbs, aorist forms (like δίδωμι)
    OMI_PR = "omi_pr"                # ο-μι verbs, present stem (like δίδωμι)
    OOS_OH_OON = "oos_oh_oon"        # Three-termination adjectives with -οος/-οη/-οον pattern  
    OOS_OON = "oos_oon"              # Two-termination adjectives with -οος/-οον pattern
    OUS_ONTOS = "ous_ontos"          # Third declension nouns with -ους/-οντος pattern
    PERF2_ACT = "perf2_act"          # Second perfect active forms
    PERFP_D = "perfp_d"              # Perfect passive with dental stems
    PERFP_G = "perfp_g"              # Perfect passive with guttural stems  
    PERFP_GG = "perfp_gg"            # Perfect passive with double guttural stems
    PERFP_GX = "perfp_gx"            # Perfect passive with guttural + sibilant stems
    PERFP_L = "perfp_l"              # Perfect passive with liquid stems
    PERFP_MP = "perfp_mp"            # Perfect passive with labial + nasal stems
    PERFP_N = "perfp_n"              # Perfect passive with nasal stems
    PERFP_P = "perfp_p"              # Perfect passive with labial stems
    PERFP_R = "perfp_r"              # Perfect passive with rhotic stems
    PERFP_S = "perfp_s"              # Perfect passive with sibilant stems
    PERFP_UN = "perfp_un"            # Perfect passive unmarked stems
    PERFP_V = "perfp_v"              # Perfect passive with vowel stems
    POUS_PODOS = "pous_podos"        # Third declension nouns with -πους/-ποδος pattern (like πούς, ποδός)
    GEOG_NAME = "geog_name"          # Geographical names and place names
    
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
            cls.AS_AINA_AN,      # Three-termination adjectives like τάλας, τάλαινα, τάλαν
            cls.EIS_ESSA,        # Three-termination adjectives with -εις, -εσσα, -εν endings
            cls.EOS_EH_EON,      # Three-termination adjectives with -εος/-εη/-εον pattern
            cls.HEIS_HESSA,      # Irregular adjectives like εἷς, μία, ἕν
            cls.HN_EINA_EN,      # Three-termination adjectives with -ην/-εινα/-εν pattern
            cls.IS_IDOS_ADJ,     # Adjectives with -ις/-ιδος pattern
            cls.IS_ITOS_ADJ,     # Adjectives with -ις/-ιτος pattern
            cls.N_NOS_ADJ,       # Adjectives with -ν/-νος pattern
            cls.OEIS_OESSA,      # Three-termination adjectives with -οεις/-οεσσα/-οεν pattern
            cls.OOS_OH_OON,      # Three-termination adjectives with -οος/-οη/-οον pattern
            cls.OOS_OON,         # Two-termination adjectives with -οος/-οον pattern
            cls.VERB_ADJ,        # Verbal adjectives (general pattern)
            cls.VERB_ADJ1,       # Verbal adjectives pattern 1
            cls.VERB_ADJ2,       # Verbal adjectives pattern 2
            cls.WN_OUSA_ON,      # Participles with -ων/-ουσα/-ον pattern
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