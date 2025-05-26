import unittest
from gd_tools.core import Morphology

class TestMorphology(unittest.TestCase):
    """
    Tests static morphology methods
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_delenition(self):
        self.assertEqual(Morphology.delenite("chrodh"), "crodh")
        self.assertEqual(Morphology.delenite("aois"), "aois")
        self.assertEqual(Morphology.delenite("a"), "a")
        self.assertEqual(Morphology.delenite("crodh"), "crodh")
        self.assertEqual(Morphology.delenite("shreap"), "sreap")
        self.assertEqual(Morphology.delenite("Bhatarsaigh"), "Bhatarsaigh")

    def test_deslenderize(self):
        self.assertEqual(Morphology.deslenderize("eilein"), "eilean")
        self.assertEqual(Morphology.deslenderize("eilean"), "eilean")
        self.assertEqual(Morphology.deslenderize("eich"), "each")

    def test_lenite(self):
        self.assertEqual(Morphology.lenite("aois"), "aois")
        self.assertEqual(Morphology.lenite("stad"), "stad")
        self.assertEqual(Morphology.lenite("sreap"), "shreap")
        self.assertEqual(Morphology.lenite("crodh"), "chrodh")

    def test_remove_final_apostrophe(self):
        self.assertEqual(Morphology.remove_final_apostrophe("bion'"), "biona")
        self.assertEqual(Morphology.remove_final_apostrophe("glic'"), "glice")
        self.assertEqual(Morphology.remove_final_apostrophe("tro'"), "tro'")
        self.assertEqual(Morphology.remove_final_apostrophe("O'"), "O'")

        
        
