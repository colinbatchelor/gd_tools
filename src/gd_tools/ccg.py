"""Mixture of generically-useful classes, UD-specific ones and CCG-specific ones."""
import os
from pathlib import Path
import re
import csv
from gd_tools.core import Lemmatizer
from gd_tools.core import Lemmatizer_xpos
from gd_tools.core import Morphology

class CCGRetagger:
    """Relies on the subcategoriser, largely."""
    def __init__(self):
        self.sub = Subcat()
        self.retaggings = {}
        with open(Path(__file__).parent / 'resources/retaggings.txt') as file:
            for line in file:
                if not line.startswith("#"):
                    tokens = line.split('\t')
                    self.retaggings[tokens[0]] = tokens[1].strip()
        self.specials = {
            'Mgr':['FIRSTNAME'], "Mghr":['FIRSTNAME'],
            'Dh’':['ADVPRE'], "Dh'":['ADVPRE'],
            'dragh':['NPROP'], 'dùil':['NPROP'],
            'Ach':['CONJ','SCONJ', 'ADVPRE'],
            'ach':['CONJ','SCONJ', 'ADVPRE'],
            'Agus':['CONJ', 'SCONJ', 'ADVPRE'],
            'agus':['CONJ', 'SCONJ', 'ADVPRE'],
            ',':['APPOS', 'NMOD', 'PUNC'],
            '-':['APPOS', 'NMOD', 'PUNC'],
            'dèidh':['N', 'NDEIDH'],
            'air':['ASPAIR', 'ASP', 'P', 'PP'],
            'ag':['ASP'],
            'rùnaire':['NAME'],
            'riaghladair':['NAME'],
            'dè':['INTERRDE'], 'i':['PRONOUN']
        }

    @staticmethod
    def retag_article(xpos):
        """Articles are N/N unless they are in the genitive in which case they are N/N/N/N"""
        return ['DET'] if not xpos.endswith('g') else ['DETNMOD']

    def retag_verb(self, surface, xpos):
        """Relies on surface."""
        return self.sub.subcat_tuple(surface, xpos)

    def retag(self, surface, rawpos):
        """Relies on surface and xpos."""
        # assume it was meant all along
        pos = rawpos.replace('*','')
        if surface.lower() in self.specials:
            return self.specials[surface.lower()]
        # separate mechanism for verbs
        if pos.startswith('Nv') or pos.startswith('V') or pos.startswith('W'):
            return self.retag_verb(surface, pos)
        # and articles
        if pos.upper().startswith('T'):
            return self.retag_article(pos)
        if pos in self.retaggings:
            return [self.retaggings[pos]]
        # for cases where we are not using all of the features
        return [self.retaggings[pos[0:2]]]

class Subcat:
    """Assigns subcategories based on lemmata."""
    def __init__(self):
        self.lemmatizer = Lemmatizer_xpos()
        self.mappings = {}
        self.mappings['default'] = ['TRANS', 'INTRANS']
        subcats = []
        with open(Path(__file__).parent / 'resources/subcat.txt') as file:
            for line in file:
                if not line.startswith('#'):
                    if re.match('^[0-9]', line):
                        tokens = line.split()
                        subcats = [t.strip() for t in tokens[1:]]
                    else:
                        self.mappings[line.strip()] = subcats

    def subcat_tuple(self, surface, pos):
        """Wrapper for subcat. Relies on lemmatizer."""
        return self.subcat(self.lemmatizer.lemmatize(surface, pos))

    def subcat(self, lemma):
        """Relies on lemma."""
        if lemma in self.mappings.keys():
            return self.mappings[lemma]
        return self.mappings["default"]


class CCGTyper:
    """Adds CCG features"""
    def __init__(self):
        """Adds CCG features"""
        self.types = {}
        with open(Path(__file__).parent / 'resources/types.txt') as file:
            for line in file:
                if not line.startswith("#"):
                    tokens = line.split('\t')
                    self.types[tokens[0]] = tokens[1].strip()

    def type_verb(self, surface, pos, tag):
        """Adds CCG features"""
        clausetypes = {"p":"dcl","s":"dcl","f":"dcl","r":"rel","d":"dep"}
        clausetype = clausetypes[pos[-1]] if pos[-1] in clausetypes \
            else "small" if pos == "Nv" else "imp"
        tense = "pres" if "p" in pos else "past" if "s" in pos \
            else "fut" if "f" in pos else "hab" if "h" in pos else None
        phon = "vowel" if re.match("^[aeiouàèìòù]", surface) or surface.startswith("f") else "cons"
        features = (clausetype if tense is None else f"{clausetype} {tense}") + f" {phon}"
        newtag = tag + features.upper().replace(' ','')
        ccg_type = self.types[tag] % features
        if pos.startswith("Vm") or '0' in pos:
            newtag = newtag + "IMPERS"
        else:
            ccg_type = ccg_type + "/n"
        return (newtag, ccg_type)

    def type(self, surface, pos, tag):
        """Retypes it as a verb if it's a verb, copula or verbal noun."""
        if pos.startswith("V") or pos.startswith("W") or pos == "Nv":
            return self.type_verb(surface, pos, tag)
        return (tag, self.types[tag])
