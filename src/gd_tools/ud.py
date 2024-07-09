import os
import csv
import re

class Features:
    """
    Assigns Scottish Gaelic UD features based on ARCOSG POS tags.
    These methods generate a dictionary as per the UD guidelines.
    """
    def __init__(self):
        self.cases = {'n':'Nom', 'd':'Dat', 'g':'Gen', 'v':'Voc'}
        self.genders = {'m':'Masc', 'f':'Fem'}
        self.numbers = {'s':'Sing', 'p':'Plur', 'd':'Dual'}
        self.numforms = {"Mn": "Digit", "Mr": "Roman"}
        self.numtypes = {"Mc": "Card", "Mo": "Ord"}
        self.tenses = {"p":"Pres", "s":"Past", "f":"Fut"}
        self.parttypes = {"Qa":"Cmpl", "Qn":"Cmpl", "Q-r":"Vb", "Qnr":"Vb", "Qq":"Vb",
                            "Qnm":"Vb", "Ua":"Ad", "Uc":"Comp", "Ug":"Inf", "Uv":"Voc",
                            "Up":"Pat", "Uo":"Num"}
        self.polartypes_q = {"Qn":"Neg", "Qnr":"Neg", "Qnm":"Neg"}
        self.prontypes_q = {"Q-r": "Rel", "Qnr": "Rel", "Qq": "Int", "Uq": "Int"}

    def feats(self, xpos: str, feats: dict, prev_xpos: str = "") -> dict:
        """
        Assign UD features based on an ARCOSG XPOS.
        """
        if xpos.startswith("A"):
            return self.feats_adj(xpos)
        if xpos == "Nv":
            return self.feats_nv(prev_xpos, xpos)
        if xpos.startswith("N"):
            return self.feats_noun(xpos, feats)
        if xpos.startswith("M"):
            return self.feats_num(xpos, feats)
        if xpos.startswith("T"):
            return self.feats_det(xpos)
        if xpos.startswith("U") or xpos.startswith("Q"):
            return self.feats_part(xpos)
        if xpos.startswith("V"):
            return self.feats_verb(xpos)
        if xpos.startswith("W"):
            return self.feats_cop(xpos)
        if xpos in ["Xfe", "Xf"]:
            return {"Foreign":["Yes"]}
        if xpos.startswith("Pp") or xpos.startswith("Px") or xpos.startswith("Dp"):
            return self.feats_pron(xpos)
        return {}

    def feats_adj(self, xpos: str) -> dict:
        """Marks degree, number, gender and case."""
        if xpos == "Apc":
            return {"Degree":["Cmp,Sup"]}
        result = {}
        if not xpos.startswith('Aq-'):
            return result
        result["Number"] = [self.numbers[xpos[3]]]
        if len(xpos) == 4:
            return result
        result["Gender"] = [self.genders[xpos[4]]]
        if len(xpos) == 5:
            return result
        result["Case"] = [self.cases[xpos[5]]]
        return result

    def feats_cop(self, xpos: str) -> dict:
        """Marks tense, mood, polarity and whether relative."""
        result = {}
        if len(xpos) > 1:
            result["Tense"] = [self.tenses[xpos[1]]]
        if len(xpos) > 2:
            if xpos[2] == "r":
                result["PronType"] = ["Rel"]
        if len(xpos) > 3:
            if xpos[3] == "q":
                result["Mood"] = ["Int"]
        if len(xpos) == 5:
            if xpos[4] == "n":
                result["Polarity"] = ["Neg"]
            elif xpos[4] == "a":
                result["Polarity"] = ["Aff"]
        return result

    def feats_det(self, xpos: str) -> dict:
        """Marks number, gender and case"""
        result = {"PronType": ["Art"], "Definite": ["Def"]}
        number = [self.numbers[xpos[2]]]
        result["Number"] = number
        if len(xpos) == 3:
            return result
        if xpos[3] != "-":
            result["Gender"] = [self.genders[xpos[3]]]
        if len(xpos) == 4:
            return result
        case = [self.cases[xpos[4]]]
        result["Case"] = case
        if xpos[3] == "-":
            return {"Case":case, "Number":number}
        return result

    def feats_noun(self, xpos: str, feats: dict) -> dict:
        """Marks case, gender, number and whether emphatic."""
        if "Typo" in feats:
            result = {"Typo":["Yes"]}
        else:
            result = {}
        if xpos in ["Nf", "Nn", "Nt"]:
            return {}
        if xpos.endswith("e"):
            result["Form"] = ["Emp"]
        if xpos[1] in ["f", "v"]:
            return result
        result["Case"] = [self.cases[xpos[4]]]
        if xpos[3] == "-":
            return result
        result["Gender"] = [self.genders[xpos[3]]]
        if xpos.startswith('Nn'):
            return result
        result["Number"] = [self.numbers[xpos[2]]]
        return result

    def feats_num(self, xpos: str, feats: dict) -> dict:
        """
        Marks NumForm and NumType based on XPOS.
        """
        result = feats
        if xpos in self.numtypes:
            result["NumType"] = [self.numtypes[xpos]]
        if xpos in self.numforms:
            result["NumForm"] = [self.numforms[xpos]]
        return result

    @staticmethod
    def feats_nv(prev_xpos: str, xpos: str) -> dict:
        """Marks whether a verbal noun or an infinitve."""
        result = {}
        if prev_xpos.startswith("Sa") or prev_xpos.startswith("Sp"):
            result["VerbForm"] = ["Vnoun"]
        elif prev_xpos == "Ug" or prev_xpos.startswith("Dp"):
            result["VerbForm"] = ["Inf"]
        else:
            result["VerbForm"] = ["Vnoun"]
        if xpos.endswith("e"):
            result["Form"] = ["Emp"]
        return result

    def feats_part(self, xpos: str) -> dict:
        """Marks particle type, mood, polarity, pronoun type, tense and mood."""
        result = {}
        if xpos in self.parttypes:
            result["PartType"] = [self.parttypes[xpos]]
        if xpos in self.polartypes_q:
            result["Polarity"] = [self.polartypes_q[xpos]]
        if xpos in self.prontypes_q:
            result["PronType"] = [self.prontypes_q[xpos]]
        if xpos == "Q--s":
            result["Tense"] = ["Past"]
        return result

    def feats_prep(self, xpos: str) -> dict:
        '''Example: Spp1s'''
        result = {}
        result["Poss"] = ["Yes"]
        result["Person"] = [xpos[3]]
        result["Number"] = [self.numbers[xpos[4]]]
        if len(xpos) > 5 and xpos[5] in self.genders:
            result["Gender"] = [self.genders[xpos[5]]]
        if xpos.endswith('e'):
            result["Form"] = ['Emp']
        return result

    def feats_pron(self, xpos: str) -> dict:
        """
        Marks for possessiveness, person, number, gender, whether emphatic and if interrogative.
        """
        result = {}
        if xpos[1] == "p" and xpos[0] == "D":
            result["Poss"] = ["Yes"]
        if len(xpos) > 2:
            result["Person"] = [xpos[2]]
            result["Number"] = [self.numbers[xpos[3]]]
        if len(xpos) > 4 and xpos[4] in self.genders:
            result["Gender"] = [self.genders[xpos[4]]]
        if xpos.endswith('e'):
            result["Form"] = ['Emp']
        if xpos in self.prontypes_q:
            result["PronType"] = [self.prontypes_q[xpos]]
        if xpos == "Px":
            result["Reflex"] = ["Yes"]
        return result

    def feats_verb(self, xpos: str) -> dict:
        """Marks for person, tense and mood."""
        result = {}
        if '0' in xpos:
            result["Person"] = ["0"]
        elif '1' in xpos:
            result["Person"] = ["1"]
        elif '2' in xpos:
            result["Person"] = ["2"]
        if len(xpos) == 2: # this may well be a mistagging
            result["Mood"] = ["Imp"]
            return result
        if xpos[2] in self.tenses:
            result["Tense"] = [self.tenses[xpos[2]]]
        if xpos[2] == "h":
            result["Mood"] = ["Cnd"]
        if xpos[1] == "m":
            result["Mood"] = ["Imp"]
        return result

