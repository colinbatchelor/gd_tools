"""Tests a mixture of generic, UD-specific and CCG-specific functions."""
import csv
import unittest
from gd_tools.acainn import CCGRetagger, CCGTyper, Subcat
from gd_tools.features import Features
from gd_tools.lemmatizer import Lemmatizer

class TestIntegration(unittest.TestCase):
    """Checks that all the labels actually match."""
    def setUp(self):
        self.retagger = CCGRetagger()
        self.subcat = Subcat()
        self.typer = CCGTyper()

    def tearDown(self):
        self.retagger = None
        self.subcat = None
        self.typer = None

    def test_retagger(self):
        """?"""
        for key in self.retagger.retaggings:
            tag = self.retagger.retaggings[key]
            self.assertTrue(tag in self.typer.types.keys())

    def test_subcat(self):
        """also ?"""
        for key in self.subcat.mappings:
            for item in self.subcat.mappings[key]:
                self.assertTrue(item in self.typer.types.keys(), item)

class TestFeatures(unittest.TestCase):
    """Tests features generated correctly in UD format."""
    def setUp(self):
        self.featuriser = Features()

    def tearDown(self):
        self.featuriser = None

    def test_feats_adj(self):
        """Checks for predicate (will break) and comparatives/superlatives."""
        self.assertEqual({}, self.featuriser.feats_adj('Ap'))
        self.assertEqual({'Degree':['Cmp,Sup']}, self.featuriser.feats_adj('Apc'))

    def test_feats_det(self):
        """Tests feature sets for determiners"""
        self.assertEqual({"Definite": ["Def"], 'Gender':['Masc'],'Number':['Sing'],
                          "PronType":["Art"]},
                         self.featuriser.feats_det('Tdsm'))
        self.assertEqual({"Definite": ["Def"], 'Gender':['Fem'],'Number':['Sing'],
                          "PronType":["Art"]},
                         self.featuriser.feats_det('Tdsf'))
        self.assertEqual({"Definite": ["Def"], 'Gender':['Masc'],'Number':['Plur'],
                          "PronType":["Art"]},
                         self.featuriser.feats_det('Tdpm'))
        self.assertEqual({"Definite": ["Def"], 'Case':['Gen'],'Gender':['Fem'], 'Number':['Plur'],
                          "PronType":["Art"]},
                         self.featuriser.feats_det('Tdpfg'))

    def test_feats_noun(self):
        """Tests feature sets for nouns."""
        self.assertEqual({'Case':['Nom'],'Gender':['Masc'],'Number':['Sing']},
                         self.featuriser.feats_noun('Ncsmn', {}))
        self.assertEqual({'Case':['Dat'],'Gender':['Fem'],'Number':['Plur']},
                         self.featuriser.feats_noun('Ncpfd', {}))
        self.assertEqual({'Case':['Gen'],'Gender':['Fem'],'Number':['Plur']},
                         self.featuriser.feats_noun('Ncpfg', {}))

class TestCCGTyper(unittest.TestCase):
    """Assigns CCG expressions based on form, xpos and subcat."""
    def setUp(self):
        self.typer = CCGTyper()

    def tearDown(self):
        self.typer = None

    def test(self):
        """Migrate to csv file."""
        self.assertEqual(self.typer.type("tha", "V-p", "BIPP")[1],
                         "s[dcl pres cons]/pp/n")
        self.assertEqual(self.typer.type("bha", "V-s", "BIPP")[1],
                         "s[dcl past cons]/pp/n")

class TestCCGRetagger(unittest.TestCase):
    """Not sure what this does after four years."""
    def setUp(self):
        self.retagger = CCGRetagger()

    def tearDown(self):
        self.retagger = None

    def test(self):
        """TODO: work out what this does"""
        self.assertTrue("ASP" in self.retagger.retag("ag", "Sa"))
        self.assertEqual(self.retagger.retag("a'", "Sa"), ["ASP"])
        agus = self.retagger.retag("agus", "Cc")
        self.assertTrue("CONJ" in agus)
        air = self.retagger.retag("air", "Sp")
        self.assertTrue("PP" in air)
        self.assertTrue("P" in air)
        self.assertEqual(self.retagger.retag("droch", "Ar"), ["DET"]) # not really
        comma = self.retagger.retag(",", "Fi")
        self.assertTrue("PUNC" in comma)
        fullstop = self.retagger.retag(".", "Fe")
        self.assertTrue("PUNC" in fullstop)
        self.assertEqual(self.retagger.retag("le", "Sp"), ["P"])
        self.assertEqual(self.retagger.retag("gun", "Qa"), ["GU"])
        self.assertEqual(self.retagger.retag("dìreach", "Rg"), ["ADV"])
        self.assertEqual(self.retagger.retag("Comhairle", "Ncsdf"), ["N"])
        self.assertEqual(self.retagger.retag("galain", "Ncsfn"), ["N"])
        self.assertEqual(self.retagger.retag("an", "Tdsf"), ["DET"])
        self.assertEqual(self.retagger.retag("na", "Tdsfg"), ["DETNMOD"])
        self.assertEqual(self.retagger.retag("[1]", "Xsc"), ["ADVPRE"])
        radh = self.retagger.retag("ràdh", "Nv")
        self.assertTrue("VPROP" in radh)
        rinn = self.retagger.retag("rinn", "V-s")
        self.assertTrue("TRANS" in rinn)
        tha = self.retagger.retag("tha", "V-p")
        self.assertTrue("BIPP" in tha)
        self.assertTrue("BIPROG" in tha)

class TestSubcat(unittest.TestCase):
    """Assigns subcategories based on PPs that verbs take."""
    def setUp(self):
        self.subcat = Subcat()

    def tearDown(self):
        self.subcat = None

    def test_lemmata(self):
        """Only subcategorises verbs."""
        self.assertEqual(self.subcat.subcat("bi"), ['BIPROG', 'BIPP'])
        self.assertEqual(self.subcat.subcat("is"), ['TRANS'])
        self.assertEqual(self.subcat.subcat("abair"), ['TRANS', 'VPROP'])
        self.assertEqual(self.subcat.subcat("arsa"), ['QUOTE'])
        cluinn = self.subcat.subcat("cluinn")
        self.assertTrue('TRANS' in cluinn)
        self.assertTrue('VPROPQ' in cluinn)
        self.assertTrue('VBHO' in cluinn)
        self.assertEqual(self.subcat.subcat("faic"), ['TRANS'])
        self.assertTrue('TRANS' in self.subcat.subcat("faigh"))
        rach = self.subcat.subcat("rach")
        self.assertTrue('INTRANS' in rach)
        self.assertTrue('RACH' in rach)
        self.assertTrue('INTRANS' in self.subcat.subcat("thig"))
        self.assertTrue('TRANS' in self.subcat.subcat("buail"))
        self.assertTrue('VRI' in self.subcat.subcat("bruidhinn"))
        self.assertTrue('VRI' in self.subcat.subcat("coinnich"))
        cuir = self.subcat.subcat("cuir")
        self.assertTrue('VAIR' in cuir)
        self.assertTrue('VRI' in cuir)
        cum = self.subcat.subcat("cùm")
        self.assertTrue('VAIR' in cum)
        self.assertTrue('VPROPQ' in cum)
        self.assertFalse('INTRANS' in self.subcat.subcat("fàg"))
        self.assertFalse('TRANS' in self.subcat.subcat("falbh"))
        self.assertTrue('FAODFEUM' in self.subcat.subcat("faod"))
        fas = self.subcat.subcat("fàs")
        self.assertTrue('INTRANS' in fas)
        self.assertTrue('VADJ' in fas)
        self.assertTrue('FAODFEUM' in self.subcat.subcat("feum"))
        self.assertTrue('VAIR' in self.subcat.subcat("fuirich"))
        self.assertFalse('INTRANS' in self.subcat.subcat("gluais"))
        self.assertTrue('VAIR' in self.subcat.subcat("iarr"))
        self.assertTrue('VPROPQ' in self.subcat.subcat("inns"))
        self.assertTrue('INTRANS' in self.subcat.subcat("obraich"))
        self.assertTrue('VAIR' in self.subcat.subcat("ruig"))
        self.assertFalse('TRANS' in self.subcat.subcat("ruith"))
        self.assertTrue('VAIR' in self.subcat.subcat("seall"))
        self.assertTrue('BIPROG' in self.subcat.subcat("tòisich"))
        self.assertTrue('VGU' in self.subcat.subcat("tionndaidh"))

    def test_ambiguous_verbs(self):
        """These are ones like coimhead that take various prepositions"""
        coimhead = self.subcat.subcat("coimhead")
        self.assertTrue('VAIR' in coimhead)
        self.assertTrue('VRI' in coimhead)
        dean = self.subcat.subcat("dèan")
        self.assertTrue('TRANS' in dean)
        self.assertTrue('VAIR' in dean)
        feuch = self.subcat.subcat("feuch")
        self.assertTrue('VRI' in feuch)
        self.assertTrue('VPROP' in feuch)
        self.assertTrue('VPROPQ' in feuch)
        gabh = self.subcat.subcat("gabh")
        self.assertTrue('VAIR' in gabh)
        self.assertTrue('VRI' in gabh)
        leig = self.subcat.subcat("leig")
        self.assertTrue('VLE' in leig)
        self.assertTrue('VDE' in leig)
        smaoinich = self.subcat.subcat("smaoinich")
        self.assertTrue('VPROP' in smaoinich)
        self.assertTrue('VMU' in smaoinich)
        tachair = self.subcat.subcat("tachair")
        self.assertTrue('IMPERS' in tachair)
        self.assertTrue('VAIR' in tachair)

if __name__ == '__main__':
    unittest.main()
