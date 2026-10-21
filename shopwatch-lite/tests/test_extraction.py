import unittest
from src.extraction import masquer_donnees
from src.extraction import lire_journal


class TestExtraction(unittest.TestCase):

    def test_masquer_donnees(self):
        self.assertEqual(
            masquer_donnees("client=bob pwd=abc123"),
            "client=bob pwd=[MASQUE]"
        )

        self.assertNotIn(
            "4970123412341234",
            masquer_donnees("card=4970123412341234")
        )
    
    def test_lire_journal(self):
        ligne = (
            "2026-11-27 17:02:11 paiement ERROR timeout "
            "card=4970123412341234"
        )

        sig = lire_journal(ligne, 42)

        self.assertEqual(sig.ref, "SH-0042")
        self.assertEqual(sig.date, "2026-11-27T17:02:11Z")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertEqual(sig.categorie, "JOURNAL")
        self.assertNotIn("4970123412341234", sig.texte)

    def test_environnement(self):
        ligne = "2026-11-27 17:02:11 paiement ERROR timeout"

        sig = lire_journal(ligne, 43, env="test")

        self.assertEqual(sig.env, "test")



if __name__ == "__main__":
    unittest.main()