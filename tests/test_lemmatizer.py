import csv
from pathlib import Path
import unittest
from gdtools.lemmatizer import Lemmatizer

class TestLemmatizer(unittest.TestCase):
    """Expects XPOS in most cases. Consider also accepting UD features."""
    def setUp(self):
        self.lemmatizer = Lemmatizer()

    def tearDown(self):
        self.lemmatizer = None

    def comparative(self, comparative, lemma):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize(comparative, "Apc"), lemma)

    def second_comparative(self, comparative, lemma):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize(comparative, "Aps"), lemma)

    def from_file(self, filename):
        """Expects form, XPOS and lemma."""
        with open(Path(__file__).parent / filename) as file:
            reader = csv.reader(file)
            next(reader)
            for line in reader:
                print(line)
                self.assertEqual(self.lemmatizer.lemmatize(line[0], line[1]), line[2])

    def from_file_fixed_xpos(self, filename, xpos):
        """For files with just form and lemma where you know the XPOS up-front."""
        with open(Path(__file__).parent / filename) as file:
            reader = csv.reader(file)
            next(reader)
            for line in reader:
                self.assertEqual(self.lemmatizer.lemmatize(line[0], xpos), line[1])

    def test_adjectives(self):
        """Expects form, XPOS and lemma."""
        self.from_file("resources/test_adjectives.csv")

    def test_adverbs(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("chaoidh", "Rt"), "chaoidh")
        self.assertEqual(self.lemmatizer.lemmatize("cho", "Rg"), "cho")
        self.assertEqual(self.lemmatizer.lemmatize("fhathast", "Rt"), "fhathast")
        self.assertEqual(self.lemmatizer.lemmatize("sheo", "Rs"), "seo")
        self.assertEqual(self.lemmatizer.lemmatize("shin", "Rs"), "sin")
        self.assertEqual(self.lemmatizer.lemmatize("shiud", "Rs"), "siud")
        self.assertEqual(self.lemmatizer.lemmatize("shuas", "Rs"), "suas")
        self.assertEqual(self.lemmatizer.lemmatize("thall", "Rs"), "thall")
        self.assertEqual(self.lemmatizer.lemmatize("thairis", "Rg"), "thairis")
        self.assertEqual(self.lemmatizer.lemmatize("thairis", "Rs"), "thairis")
        self.assertEqual(self.lemmatizer.lemmatize("thric", "Rt"), "tric")

    def test_comparatives(self):
        """TODO: move to csv"""
        self.comparative("àille", "àlainn")
        self.comparative("àirde", "àrd")
        self.comparative("aotruime", "aotrom")
        self.comparative("bige", "beag")
        self.comparative("caime", "cam")
        self.comparative("comasaiche", "comasach")
        self.comparative("cudromaiche", "cudromach")
        self.comparative("dealasaich", "dealasach")
        self.comparative("dhorcha", "dorcha")
        self.comparative("dlùithe", "dlùth")
        self.comparative("duirche", "dorcha")
        self.comparative("fhaide", "fada")
        self.comparative("fhaid'", "fada")
        self.comparative("fhaisge", "faisg")
        self.comparative("fhaisg'", "faisg")
        self.comparative("fhasa", "furasta")
        self.comparative("fhèarr", "math")
        self.comparative("fhearr", "math")
        self.comparative("fheàrr", "math")
        self.comparative("fuaire", "fuar")
        self.comparative("iomchaidhe", "iomchaidh")
        self.comparative("ìsle", "ìosal")
        self.comparative("làidire", "làidir")
        self.comparative("leatha", "leathann")
        self.comparative("luaithe", "luath")
        self.comparative("lugha", "beag")
        self.comparative("mheasaile", "measail")
        self.comparative("mhò", "mòr")
        self.comparative("mhuth'", "mòr")
        self.comparative("miona", "mion")
        self.comparative("miosa", "dona")
        self.comparative("motha", "math")
        self.comparative("òige", "òg")
        self.comparative("nitheile", "nitheil")
        self.comparative("righne", "righinn")
        self.comparative("righinne", "righinn")
        self.comparative("shaoire", "saor")
        self.comparative("shine", "sean")
        self.comparative("sine", "sean")
        self.comparative("taitniche", "taitneach")
        self.comparative("tràithe", "tràth")
        self.comparative("trice", "tric")
        self.second_comparative("fheàirrde", "math")
        self.second_comparative("mhisde", "dona")

    def test_interjections(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("bhuel", "I"), "bhuel")
        self.assertEqual(self.lemmatizer.lemmatize("shìorraidh", "I"), "sìorraidh")
        self.assertEqual(self.lemmatizer.lemmatize("uh", "I"), "uh")

    def test_nouns(self):
        """Verbal nouns are in a separate test."""
        print(Path(__file__))

        self.from_file('resources/test_nouns.csv')

    def test_copula(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("an", "Wpdqa"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("B'", "Ws"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("b'", "Ws"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("bu", "Ws"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("cha", "Wp-in"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("chan", "Wp-in"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("gur", "Wpdia"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("'S", "Wp-i"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("'s", "Wp-i"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("is", "Wp-i"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("nach", "Wpdqn"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("'se", "Wp-i-3"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("as", "Wpr"), "is")

    def test_particles(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("d’", "Q--s"), "do")
        self.assertEqual(self.lemmatizer.lemmatize("'g", "Sa"), "ag")

    def test_prefixed_words(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("h-Alba", "Nt"), "Alba")
        self.assertEqual(self.lemmatizer.lemmatize("dh’aon", "Mc"), "aon")
        self.assertEqual(self.lemmatizer.lemmatize("n-eachdraidh", "Ncsfd"),
                         "eachdraidh")
        self.assertEqual(self.lemmatizer.lemmatize("t-seòrsa", "Ncsmd"), "seòrsa")

    def test_prepositions(self):
        """Examples in the file may also be Nf."""
        self.from_file('resources/test_nouns.csv')

    def test_copula(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("an", "Wpdqa"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("B'", "Ws"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("b'", "Ws"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("bu", "Ws"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("cha", "Wp-in"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("chan", "Wp-in"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("gur", "Wpdia"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("'S", "Wp-i"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("'s", "Wp-i"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("is", "Wp-i"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("nach", "Wpdqn"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("'se", "Wp-i-3"), "is")
        self.assertEqual(self.lemmatizer.lemmatize("as", "Wpr"), "is")

    def test_particles(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("d’", "Q--s"), "do")
        self.assertEqual(self.lemmatizer.lemmatize("'g", "Sa"), "ag")

    def test_prefixed_words(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("h-Alba", "Nt"), "Alba")
        self.assertEqual(self.lemmatizer.lemmatize("dh’aon", "Mc"), "aon")
        self.assertEqual(self.lemmatizer.lemmatize("n-eachdraidh", "Ncsfd"),
                         "eachdraidh")
        self.assertEqual(self.lemmatizer.lemmatize("t-seòrsa", "Ncsmd"), "seòrsa")

    def test_prepositions(self):
        """Examples in the file may also be Nf."""
        self.from_file_fixed_xpos('resources/test_prepositions.csv', 'Sp')

    def test_pronouns(self):
        """TODO: move to csv"""
        self.assertEqual(self.lemmatizer.lemmatize("chéile", "Px"), "céile")
        self.assertEqual(self.lemmatizer.lemmatize("chèile", "Px"), "cèile")
        self.assertEqual(self.lemmatizer.lemmatize("fhéin", "Px"), "féin")
        self.assertEqual(self.lemmatizer.lemmatize("fhèin", "Px"), "fèin")
        self.assertEqual(self.lemmatizer.lemmatize("fhìn", "Px"), "fèin")

    def test_verbal_nouns(self):
        """These lemmatize to the verb root."""
        self.from_file_fixed_xpos('resources/test_verbal_nouns.csv', "Nv")

    def test_verbs(self):
        """Requires form, XPOS and lemma from file."""
        self.from_file('resources/test_verbs.csv')

if __name__ == '__main__':
    unittest.main()
