"""
Lemmatizer for Scottish Gaelic which largely relies on XPOS information.
"""
import os
import csv
import re

class Lemmatizer:
    """
    The POS tags are taken from ARCOSG.
    For future-proofing it would be good to support other UD fields.
    """
    def __init__(self):
        folder = os.path.dirname(__file__)
        self.prepositions = {}
        prep_path = os.path.join(folder, 'resources', 'prepositions.csv')
        with open(prep_path) as file:
            reader = csv.reader(file)
            for row in reader:
                self.prepositions[row[0]] = row[1]
        self.possessives = {
            "Dp1s": "mo", "Dp2s": "do", "Dp3s": "a",
            "Dp1p": "ar", "Dp2p": "ur", "Dp3p": "an"
        }
        self.pronouns = {
            "mi": ["mise"], "thu": ["tu", "tusa", "thusa"],
            "e": ["esan"], "i": ["ise"],
            "sinn": ["sinne"], "sibh": ["sibhse"], "iad": ["iadsan"],
            "fèin": ["fhìn"]
            }

        vn_path = os.path.join(folder, 'resources', 'verbal_nouns.csv')
        self.vns = []
        with open(vn_path) as file:
            reader = csv.reader(file)
            for row in reader:
                self.vns.append((row[0], row[1].split(";")))
        lemmata_path = os.path.join(folder, 'resources', 'lemmata.csv')
        self.lemmata = {}
        with open(lemmata_path) as file:
            reader = csv.reader(filter(lambda row: row[0] != '#', file))
            for row in reader:
                self.lemmata[row[0]] = row[1]

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

    def lemmatize_adjective(self, surface: str, xpos: str) -> str:
        """The small number of special plurals are dealt with in lemmata.csv"""
        if xpos in ["Apc", "Aps"]:
            return self.lemmatize_comparative(surface)
        surface = self.delenite(surface)
        surface = self.remove_apostrophe(surface)
        if surface in self.lemmata:
            return self.lemmata[surface]
        if xpos == "Av":
            return re.sub("(is)?[dt][ae]?$", "", surface)
        if surface.endswith("òir"):
            return re.sub("òir$", "òr", surface)
        return surface

    def lemmatize_comparative(self, surface: str) -> str:
        """Relies on external file. If surface not in file delenites and slenderises."""
        if surface in self.lemmata:
            return self.lemmata[surface]
        if re.match(".*i[cgl]e$",surface):
            return re.sub("(i[cgl])e$", r"\1", surface)
        return re.sub("e$", "", self.delenite(self.deslenderize(surface)))

    def lemmatize_proper_noun(self, surface: str, oblique: bool) -> str:
        """May need xpos information to deal with the vocative."""
        surface = self.delenite(surface)
        if surface in ["Dougie", "Josie", "Morris"]:
            return surface
        if surface == "lain": # special case for ARCOSG
            return "Iain"
        if surface == "a'":
            return "an"
        surface = surface.replace("Mic", "Mac")
        if surface in self.lemmata:
            return self.lemmata[surface]
        if oblique and surface not in ["Iain", "Keir", "Magaidh"]:
            return self.deslenderize(surface)
        return surface

    def lemmatize_noun(self, surface: str, xpos: str) -> str:
        """
        Master function which uses other functions for Nc, Nn, Nt and Nv.
        Nf is _usually_ more like a preposition so is dealt with elsewhere.
        """
        oblique = re.match('.*[vdg]$', xpos)
        if xpos.startswith("Nn"):
            return self.lemmatize_proper_noun(surface, oblique)

        surface = self.delenite(surface)

        surface = self.remove_apostrophe(surface)
        if surface in self.lemmata:
            return self.lemmata[surface]

        if xpos.endswith("e"):
            surface = re.sub('-?san$', '', surface)

        if xpos == "Nv":
            return self.lemmatize_vn(surface)
        if xpos == "Nt":
            return "Alba" if surface in ["Albann", "Albainn"] else surface
        return self.lemmatize_common_noun(surface, xpos, oblique)

    def lemmatize_common_noun(self, surface: str, xpos: str, oblique: bool) -> str:
        """Looks as if it needs to be refactored."""
        if surface.startswith("luchd"):
            return surface.replace("luchd", "neach")
        if surface.startswith("'"):
            surface = self.delenite(surface[1:])

        plural_replacements = [
            ('eachan', 'e'), ('achan', 'a'), ('aich', 'ach'),
            ('aidhean', 'adh'), ('aichean', 'ach'), ('ichean', 'iche'),
            ('ean', ''), ('eannan', 'e'), ('ean', ''),
            ("thchannan", "thaich"),
            ('annan', 'a'), ("thran", "thar"), ("an", ""),
            ("oill", "all"), ("uill", "all"), ("ait", "at"),
            # might just be caorach
            ("ach", "a")
            ]

        if xpos.startswith("Ncp"):
            surface = re.sub("aibh$", "", surface)
            for replacement in plural_replacements:
                if surface.endswith(replacement[0]):
                    return re.sub(f"{replacement[0]}$", replacement[1], surface)
        m_replacements = [('aich', 'ach'), ('aidh', 'adh'), ('ais', 'as'), ('uis', 'us')]
        f_replacements = [('eig', 'eag'), ('eige', 'eag'), ('the', 'th')]
        if oblique and 'f' in xpos:
            for replacement in f_replacements:
                if surface.endswith(replacement[0]):
                    return re.sub(f"{replacement[0]}$", replacement[1], surface)
        if oblique and 'm' in xpos:
            for replacement in m_replacements:
                if surface.endswith(replacement[0]):
                    return re.sub(f"{replacement[0]}$", replacement[1], surface)
        if re.match(".*[bcdfghlmnprst]ich$", surface):
            return re.sub("ich$", "each", surface)
        return surface

    def lemmatize_possessive(self, xpos: str) -> str:
        """Does not look at the surface, only the POS tag."""
        return self.possessives[xpos[0:4]]

    def lemmatize_preposition(self, surface: str) -> str:
        """Relies on resources/prepositions.csv"""
        if surface.startswith("'") and len(surface) > 1:
            surface = surface[1:]
        surface = self.remove_apostrophe(surface.replace(' ', '_'))
        surface = re.sub('^h-', '', surface)
        if not re.match("^'?s[ae]n?$", surface):
            surface = re.sub("-?s[ae]n?$", "", surface)
        for pattern in self.prepositions:
            if re.match("^("+pattern+")$", surface):
                return self.prepositions[pattern]
        return "bho" if surface.startswith("bh") else self.delenite(surface)

    def lemmatize_pronoun(self, surface: str) -> str:
        """Consider rewriting based on POS tag."""
        for key in self.pronouns:
            if surface in self.pronouns[key]:
                return key
        if surface.startswith("fh") or surface.startswith("ch"):
            return self.delenite(surface)
        return surface

    def lemmatize_verb(self, surface: str, xpos: str) -> str:
        """Hybrid replacement dictionary/XPOS method."""
        for form in self.lemmata:
            if surface == form:
                return self.lemmata[form]
        replacements = [
            ("Vm-1p", "e?amaid$"), ("Vm-2p", "a?ibh$"),
            ("V-s0", "e?adh$"), ("V-p0", "e?a[rs]$"), ("V-f0", "e?ar$"),
            ("V-h", "e?adh$"), ("Vm-3", "e?adh$"), ("V-f", "a?(idh|s)$")
        ]

        if xpos.endswith("r"): # relative form
            surface = self.delenite(surface)
            if surface.endswith("eas"):
                return surface.replace("eas","")
            if surface.endswith("as"):
                return surface.replace("as","")
        else:
            for replacement in replacements:
                if xpos.startswith(replacement[0]):
                    surface = self.delenite(surface)
                    return re.sub(replacement[1], "", surface)

        return self.delenite(surface)

    def lemmatize_vn(self, surface: str) -> str:
        """Hybrid replacement dictionary/XPOS method"""
        if surface.startswith("'"):
            surface = surface[1:]
        for verbal_noun in self.vns:
            if self.delenite(surface) in verbal_noun[1]:
                return verbal_noun[0]
        replacements = [
            ('sinn', ''), ('tail', ''), ('ail', ''), ('eil', ''), ('eal', ''),
            ('aich', ''), ('ich', ''), ('tainn', ''), ('tinn', ''),
            ('eamh', ''), ('amh', ''),
            ('eamhainn', ''), ('mhainn', ''), ('inn', ''), ('eachdainn', 'ich'),
            ('eachadh', 'ich'), ('achadh', 'aich'), ('airt', 'air'),
            ('gladh', 'gail'), ('eadh', ''), ('-adh', ''), ('adh', ''),
            ('e', ''), ('eachd', 'ich'), ('achd', 'aich')
        ]
        for replacement in replacements:
            if surface.endswith(replacement[0]):
                return self.delenite(surface.replace(replacement[0], replacement[1]))
        return self.delenite(surface)

    @staticmethod
    def remove_apostrophe(surface: str) -> str:
        """Makes a guess based on slenderness of last vowel"""
        if surface.endswith("'") and surface != "a'":
            result = re.sub("'$", "", surface)
            stem = re.sub("[bcdfghlmnprst]+'$", "", surface)
            if re.match(".*[aouàòù]$", stem):
                return "%sa" % result
            return "%se" % result
        return surface

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
        if xpos.startswith("R") or xpos == "I":
            if surface not in ["bhuel", "chaoidh", "cho", "fhathast", "mhmm",
                               "thall", "thairis", "thì"]:
                return self.delenite(surface)
        if xpos[0:2] in ["Ap", "Aq", "Ar", "Av"]:
            return self.lemmatize_adjective(surface, xpos)
        if xpos[0:2] in ["Sa", "Sp", "Pr", "Nf"]:
            return self.lemmatize_preposition(surface)
        if xpos.startswith("Pp") or xpos == "Px":
            return self.lemmatize_pronoun(surface)
        if xpos.startswith("V"):
            return self.lemmatize_verb(surface, xpos)
        if xpos.startswith("N"):
            return self.lemmatize_noun(surface, xpos)
        if xpos.startswith("Dp"):
            return self.lemmatize_possessive(xpos)
        return surface
