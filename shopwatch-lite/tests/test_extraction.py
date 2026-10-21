import unittest
from src.extraction import masquer_donnees
from src.extraction import lire_journal
from src.extraction import lire_scan
from src.extraction import lire_build


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

    
    def test_lire_scan(self):
        rapport = {
            "date": "2026-11-27T17:05:00Z",
            "service": "paiement",
            "gravite": "MAJEUR",
            "faille": "CVE-2026-1234",
            "texte": "Faille connue dans une dependance"
        }

        sig = lire_scan(rapport, 44)

        self.assertEqual(sig.ref, "SH-0044")
        self.assertEqual(sig.origine, "SCANNER")
        self.assertEqual(sig.categorie, "FAILLE")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertEqual(sig.etat, "RECU")

    
    def test_lire_build_echec(self):
        rapport = {
            "date": "2026-11-27T17:10:00Z",
            "service": "paiement",
            "statut": "ECHEC",
            "texte": "Erreur de compilation"
        }

        sig = lire_build(rapport, 45)

        self.assertEqual(sig.origine, "BUILD")
        self.assertEqual(sig.categorie, "BUILD_ECHEC")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertEqual(sig.etat, "RECU")

    def test_lire_build_ok(self):
        rapport = {
            "date": "2026-11-27T17:15:00Z",
            "service": "paiement",
            "statut": "OK",
            "texte": "Build termine avec succes"
        }

        sig = lire_build(rapport, 46)

        self.assertEqual(sig.origine, "BUILD")
        self.assertEqual(sig.categorie, "BUILD_OK")
        self.assertEqual(sig.gravite, "MINEUR")
        self.assertEqual(sig.etat, "RECU")


if __name__ == "__main__":
    unittest.main()