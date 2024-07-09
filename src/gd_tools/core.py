import os
import csv
import re

class Core:
    """
    Static methods shared between classes.
    """
    @staticmethod
    def replace_ending(replacements: dict, surface) -> str:
        for key in replacements:
            if surface.endswith(key):
                return re.sub(key + "$", replacements[key], surface)
        return surface

class GOC:
    """
    Normaliser for pre-GOC texts.
    """
    def normalise(self, surface: str) -> str:
        result = self.standardise_schwa(re.sub(r"ó", "ò", re.sub(r"é", "è", surface)))
        result = re.sub(r"^str", "sr", result)
        return self.normalise_specials(result)

    def normalise_spacing(self, surface: str) -> str:
        if surface == "d'a":
            return "da"
        return re.sub("'([ei])", r"' \1", surface)

    def normalise_specials(self, surface: str) -> str:
        specials = {"aghart": "adhart", "maith": "math", "so": "seo",
                    "tigh": "taigh",
                    "timchioll": "timcheall"}
        shpecials = {}
        for key in specials:
            shpecials[Morphology.lenite(key)] = Morphology.lenite(specials[key])
        if surface in specials:
            return specials[surface]
        if surface in shpecials:
            return shpecials[surface]
        return surface

    def restore_accents(self, surface: str) -> str:
        if surface.lower() in ["fhearr", "paipear", "paipeir", "ard", "thainig"]:
            return re.sub("a", "à", surface, count = 1)
        if surface.lower() in ["duthcha", "duthaich"]:
            return re.sub("u", "ù", surface, count = 1)
        if surface in ["Eireann", "Eirinn"]:
            return re.sub("E", "È", surface, count = 1)
        return surface

    def standardise_schwa(self, surface: str) -> str:
        if surface in ["Agus", "agus"]:
            return surface
        replacements = { "uidh": "aidh", "uinn": "ainn", "uis": "ais", "um": "am", "us": "as" }
        return Core.replace_ending(replacements, surface)

class Morphology:
    """
    Static methods
    """
    @staticmethod
    def can_follow_de(surface: str) -> bool:
        """this is dè the interrogative"""
        return surface in ["cho", "am", "an", "a'", "na", "mar", "bha", "tha"]

    @staticmethod
    def delenite(surface: str) -> str:
        """Removes h as the second letter except for special cases."""
        if len(surface) < 3:
            return surface
        if surface in ["Shaw", "Christie"]:
            return surface
        return surface[0] + surface[2:] if surface[1] == 'h' else surface

    @staticmethod
    def deslenderize(surface: str) -> str:
        """Converts from slender to broad."""
        if re.match('.*ei.h?$', surface):
            return re.sub("(.*)ei(.h?)", r"\1ea\2", surface)
        if re.match('.*[bcdfghmnprst]i.h?e?$', surface):
            return re.sub("(.*)i(.h?)e?", r"\1ea\2", surface)
        return re.sub("(.*[aiouàòù])i([bcdfghmnpqrst]+)[e']?$", r"\1\2", surface)

    @staticmethod
    def is_lenited(surface: str) -> bool:
        """
        Generic test for whether the orthographic form of a word has been lenited.

        Words beginning with n, l and r also lenite but this is orthographically silent.
        """
        unlenitable = re.match(r"[AEIOUaeiouLlNnRr]|[Ss][gpt]", surface)
        return bool(unlenitable) | (surface[1] == 'h')

    @staticmethod
    def is_lenited_by_cha(surface: str) -> bool:
        """There are different rules for lenition after cha."""
        unlenitable = surface.match(r"[AEIOUaeiouLlNnRrDTSdts]")
        return unlenitable | (surface[1] == 'h')

    @staticmethod
    def is_lenited_by_dental(surface: str) -> bool:
        unlenitable = surface.match(r"[AEIOUaeiouDdTtNnRrSs]")
        return unlenitable | (surface[1] == 'h')

    @staticmethod
    def lenite(surface: str) -> str:
        """Inserts an h according to the orthographic lenition rules"""
        if Morphology.is_lenited(surface):
            return surface
        else:
            return surface[0] + "h" + surface[1:]
    
    @staticmethod
    def remove_final_apostrophe(surface: str) -> str:
        """Makes a guess based on slenderness of last vowel"""
        if surface.endswith("'") and surface != "a'":
            result = re.sub("'$", "", surface)
            stem = re.sub("[bcdfghlmnprst]+'$", "", surface)
            if re.match(".*[aouàòù]$", stem):
                return "%sa" % result
            return "%se" % result
        return surface

class Lemmatizer:
    """
    Lemmatizer for Scottish Gaelic which only uses surface information.
    """
    def __init__(self):
        folder = os.path.dirname(__file__)
        lemmata_path = os.path.join(folder, 'resources', 'lemmata.csv')
        self.lemmata = {}
        with open(lemmata_path) as file:
            reader = csv.reader(filter(lambda row: row[0] != '#', file))
            for row in reader:
                self.lemmata[row[0]] = row[1]
        pronouns = {
            "mi": ["mise"], "thu": ["tu", "tusa", "thusa"],
            "e": ["esan"], "i": ["ise"],
            "sinn": ["sinne"], "sibh": ["sibhse"], "iad": ["iadsan"],
            "fèin": ["fhìn"]
        }
        self.pronouns = {}
        for key in pronouns:
            for value in pronouns[key]:
                self.pronouns[value] = key
        self.prepositions = {}
        prep_path = os.path.join(folder, 'resources', 'prepositions.csv')
        with open(prep_path) as file:
            reader = csv.reader(file)
            for row in reader:
                self.prepositions[row[0]] = row[1]

    def lemmatize_comparative(self, surface: str) -> str:
        """If surface not in file delenites and slenderises."""
        if surface in self.lemmata:
            return self.lemmata[surface]
        surface = Morphology.delenite(surface)
        if re.match(".*i[cgl]e$",surface):
            return re.sub("(i[cgl])e$", r"\1", surface)
        return re.sub("e$", "", Morphology.deslenderize(surface))

    def lemmatize_conjunction(self, surface: str) -> str:
        """
        Lemmatizes the conjunction in 'surface'
        """
        if surface == "'s":
            return "is"
        return surface

    def lemmatize_preposition(self, surface: str) -> str:
        """
        Lemmatizes the preposition in 'surface'
        """
        if surface.startswith("'") and len(surface) > 1:
            surface = surface[1:]
        surface = Morphology.remove_final_apostrophe(surface.replace(' ', '_'))
        surface = re.sub('^h-', '', surface)
        if not re.match("^'?s[ae]n?$", surface):
            surface = re.sub("-?s[ae]n?$", "", surface)
        for pattern in self.prepositions:
            if re.match("^("+pattern+")$", surface):
                return self.prepositions[pattern]
        return "bho" if surface.startswith("bh") else Morphology.delenite(surface)

    def lemmatize_pronoun(self, surface: str) -> str:
        """Consider rewriting based on POS tag."""
        if surface in self.pronouns:
            return self.pronouns[surface]
        if surface.startswith("fh") or surface.startswith("ch"):
            return Morphology.delenite(surface)
        return surface

class Lemmatizer_xpos:
    """
    Lemmatizer for Scottish Gaelic which largely relies on XPOS information.

    The POS tags are taken from ARCOSG.
    For future-proofing it would be good to support other UD fields
    (possibly by going through a UD to XPOS mapping first).
    """
    def __init__(self):
        folder = os.path.dirname(__file__)
        self.possessives = {
            "Dp1s": "mo", "Dp2s": "do", "Dp3s": "a",
            "Dp1p": "ar", "Dp2p": "ur", "Dp3p": "an"
        }
        self.lemmatizer = Lemmatizer()
        vn_path = os.path.join(folder, 'resources', 'verbal_nouns.csv')
        vns = {}
        with open(vn_path) as file:
            reader = csv.reader(file)
            for row in reader:
                vns[row[0]] = row[1].split(";")
        self.vns = {}
        for key in vns:
            for value in vns[key]:
                self.vns[value] = key
        lemmata_path = os.path.join(folder, 'resources', 'lemmata.csv')
        self.lemmata = {}
        with open(lemmata_path) as file:
            reader = csv.reader(filter(lambda row: row[0] != '#', file))
            for row in reader:
                self.lemmata[row[0]] = row[1]

    def lemmatize_adjective(self, surface: str, xpos: str) -> str:
        """The small number of special plurals are dealt with in lemmata.csv"""
        if xpos in ["Apc", "Aps"]:
            return self.lemmatizer.lemmatize_comparative(surface)
        surface = Morphology.delenite(surface)
        surface = Morphology.remove_final_apostrophe(surface)
        if surface in self.lemmata:
            return self.lemmata[surface]
        if xpos == "Av":
            return re.sub("(is)?[dt][ae]?$", "", surface)
        if surface.endswith("òir"):
            return re.sub("òir$", "òr", surface)
        return surface

    def lemmatize_common_noun(self, surface: str, xpos: str, oblique: bool) -> str:
        """Looks as if it needs to be refactored."""
        if surface.startswith("luchd"):
            return surface.replace("luchd", "neach")

        plural_replacements = {
            "eachan": "e", "achan": "a", "aich": "ach",
            "aidhean": "adh", "aichean": "ach", "ichean": "iche",
            "eannan": "e",
            "thchannan": "thaich",
            "annan": "a", "thran": "thar",
            "oill": "all", "uill": "all", "ait": "at",
            "ach": "a",             # might just be caorach
            "rìghrean": "rìgh",
            "ean": "", "an": ""
            }

        if xpos.startswith("Ncp"):
            surface = re.sub("aibh$", "", surface)
            surface = Core.replace_ending(plural_replacements, surface)
        f_replacements = {'eig': 'eag', 'eige': 'eag', 'the': 'th'}
        if oblique and 'f' in xpos:
            surface = Core.replace_ending(f_replacements, surface)
        m_replacements = {'aich': 'ach', 'aidh': 'adh', 'ais': 'as', 'uis': 'us'}
        if oblique and 'm' in xpos:
            surface = Core.replace_ending(m_replacements, surface)
        if re.match(".*[bcdfghlmnprst]ich$", surface):
            return re.sub("ich$", "each", surface)
        return surface

    def lemmatize_noun(self, surface: str, xpos: str) -> str:
        """
        Normalises surface using part-of-speech information in xpos.

        Master function which uses other functions for Nc, Nn, Nt and Nv.
        Nf ("fossilised noun") is _usually_ more like a preposition so is dealt with elsewhere.
        """
        oblique = re.match('.*[vdg]$', xpos)
        if surface.startswith("'"):
            surface = surface[1:]
        surface = Morphology.delenite(surface)
        surface = Morphology.remove_final_apostrophe(surface)
        if xpos.startswith("Nn"):
            return self.lemmatize_proper_noun(surface, oblique)

        if surface in self.lemmata:
            return self.lemmata[surface]

        if xpos.endswith("e"):
            surface = re.sub("-?san$", "", surface)

        if xpos == "Nv":
            return self.lemmatize_vn(surface)
        if xpos == "Nt":
            return "Alba" if surface in ["Albann", "Albainn"] else surface
        return self.lemmatize_common_noun(surface, xpos, oblique)

    def lemmatize_possessive(self, xpos: str) -> str:
        """Does not look at the surface, only the POS tag."""
        return self.possessives[xpos[0:4]]

    def lemmatize_proper_noun(self, surface: str, oblique: bool) -> str:
        """
        Lemmatises surface assuming it is a proper noun.
        oblique is true if the part-of-speech information tells us the noun is in the dative, genitive or vocative.
        """
        if surface in ["Dougie", "Josie", "Morris"]:
            return surface
        if surface == "lain": # special case for ARCOSG
            return "Iain"
        if surface == "a'":
            return "an"
        surface = surface.replace("Mic", "Mac")
        if oblique and surface not in ["Iain", "Keir", "Magaidh"]:
            return Morphology.deslenderize(surface)
        return surface

    def lemmatize_verb(self, surface: str, xpos: str) -> str:
        """Hybrid replacement dictionary/XPOS method."""
        if surface in self.lemmata:
            return self.lemmata[surface]
        replacements = [
            ("Vm-1p", "e?amaid$"), ("Vm-2p", "a?ibh$"),
            ("V-s0", "e?adh$"), ("V-p0", "e?a[rs]$"), ("V-f0", "e?ar$"),
            ("V-h", "e?adh$"), ("Vm-3", "e?adh$"), ("V-f", "a?(idh|s)$")
        ]
        surface = Morphology.delenite(surface)
        relative_replacements = { "eas": "", "as": "" }
        if xpos.endswith("r"): # relative form
            return Core.replace_ending(relative_replacements, surface)
        else:
            for replacement in replacements:
                if xpos.startswith(replacement[0]):
                    return re.sub(replacement[1], "", surface)
        return surface

    def lemmatize_vn(self, surface: str) -> str:
        """
        Lemmatizes surface of a verbal noun.
        """
        if surface in self.vns:
            print(surface)
            return self.vns[surface]
        vn_replacements = {
            "sinn": "", "tail": "", "ail": "", "eil": "", "eal": "",
            "aich": "", "tich": "teachd", "ich": "", "tainn": "", "tinn": "",
            "eamh": "", "amh": "",
            "eamhainn": "", "mhainn": "", "inn": "", "eachdainn": "ich",
            "eachadh": "ich", "achadh": "aich", "airt": "air",
            "gladh": "gail", "eadh": "", "-adh": "", "adh": "",
            "e": "", "eachd": "ich", "achd": "aich"
        }
        return Core.replace_ending(vn_replacements, surface)

    def lemmatize(self, surface: str, xpos: str) -> str:
        """Lemmatize surface based on xpos."""
        surface = surface.replace('\xe2\x80\x99', "'").replace('\xe2\x80\x98', "'")
        surface = re.sub("[’‘]", "'", surface)
        surface = re.sub("^(h-|t-|n-|[Dd]h')", "", surface)
        specials = [("Q--s", "do"), ("W", "is"), ("Csw", "is"), ("Td", "an")]
        for special in specials:
            if xpos.startswith(special[0]):
                return special[1]
        if xpos[0:2] not in ["Nn", "Nt", "Up", "Y"]:
            surface = surface.lower()
        if xpos == "Cc":
            return self.lemmatizer.lemmatize_conjunction(surface)
        if xpos.startswith("R") or xpos == "I":
            if surface not in ["bhuel", "chaoidh", "cho", "fhathast", "mhmm",
                               "thall", "thairis", "thì"]:
                return Morphology.delenite(surface)
        if xpos[0:2] in ["Ap", "Aq", "Ar", "Av"]:
            return self.lemmatize_adjective(surface, xpos)
        if xpos[0:2] in ["Sa", "Sp", "Pr", "Nf"]:
            return self.lemmatizer.lemmatize_preposition(surface)
        if xpos.startswith("Pp") or xpos == "Px":
            return self.lemmatizer.lemmatize_pronoun(surface)
        if xpos.startswith("V"):
            return self.lemmatize_verb(surface, xpos)
        if xpos.startswith("N"):
            return self.lemmatize_noun(surface, xpos)
        if xpos.startswith("Dp"):
            return self.lemmatize_possessive(xpos)
        return surface
