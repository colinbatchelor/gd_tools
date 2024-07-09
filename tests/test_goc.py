import unittest
from gd_tools.core import GOC

class TestNormalise(unittest.TestCase):
    """Tests normalisation of pre-GOC text"""
    def setUp(self):
        self.goc = GOC()

    def tearDown(self):
        self.goc = None

    def test_accents(self):
        self.assertEqual("àrd", self.goc.restore_accents("ard"))
        self.assertEqual("dèidh", self.goc.normalise("déidh"))
        self.assertEqual("dùthcha", self.goc.restore_accents("duthcha"))
        self.assertEqual("Èirinn", self.goc.restore_accents("Eirinn"))
        self.assertEqual("fheàrr", self.goc.restore_accents("fhearr"))
        self.assertEqual("fhèin", self.goc.normalise("fhéin"))
        self.assertEqual("mòr", self.goc.normalise("mór"))
        self.assertEqual("pàipear", self.goc.restore_accents("paipear"))
        self.assertEqual("thàinig", self.goc.restore_accents("thainig"))

    def test_miscellany(self):
        self.assertEqual("adhart", self.goc.normalise("aghart"))        
        self.assertEqual("math", self.goc.normalise("maith"))
        self.assertEqual("seo", self.goc.normalise("so"))
        self.assertEqual("sreap", self.goc.normalise("streap"))
        self.assertEqual("sreapadh", self.goc.normalise("streapadh"))
        self.assertEqual("sruthan", self.goc.normalise("struthan"))
        self.assertEqual("thimcheall", self.goc.normalise("thimchioll"))
        self.assertEqual("taigh", self.goc.normalise("tigh"))

    def test_schwa(self):
        self.assertEqual("agus", self.goc.normalise("agus"))
        self.assertEqual("chomhnaidh", self.goc.normalise("chomhnuidh"))
        self.assertEqual("fianais", self.goc.normalise("fianuis"))
        self.assertEqual("madainn", self.goc.normalise("maduinn"))

    def test_spacing(self):
        self.assertEqual("b' e", self.goc.normalise_spacing("b'e"))
        self.assertEqual("b' i", self.goc.normalise_spacing("b'i"))
        self.assertEqual("da", self.goc.normalise_spacing("d'a"))

if __name__ == '__main__':
    unittest.main()

