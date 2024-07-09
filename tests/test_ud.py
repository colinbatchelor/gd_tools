import unittest
from gd_tools.ud import Features

class TestFeatures(unittest.TestCase):
    """
    Tests features generated correctly in UD format from the ARCOSG XPOS.
    """
    def setUp(self):
        self.featuriser = Features()

    def tearDown(self):
        self.featuriser = None

    def test_feats(self):
        """"This is the generic one which calls the featurisers for individual parts of speech"""
        self.assertEqual({"Tense": ["Pres"]}, self.featuriser.feats("V-p", {}))
        self.assertEqual({"Mood": ["Cnd"]}, self.featuriser.feats("V-h", {}))

        self.assertEqual({"PronType": ["Int"]}, self.featuriser.feats("Uq", {}))
        self.assertEqual({"Case": ["Dat"], "Gender": ["Masc"], "Number": ["Sing"]},
                         self.featuriser.feats("Ncsmd", {}))
        self.assertEqual({"Case": ["Nom"], "Gender": ["Masc"], "Number": ["Sing"]},
                         self.featuriser.feats("Aq-smn", {}))
        self.assertEqual({"Form": ["Emp"], "Gender": ["Masc"], "Number": ["Sing"], "Person": ["3"]},
                         self.featuriser.feats("Pp3sm-e", {}))

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

if __name__ == '__main__':
    unittest.main()
