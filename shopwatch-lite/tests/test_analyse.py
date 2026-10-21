import unittest

from src.analyse import est_repete
from src.contrat import Signal


def sig(date="2026-11-27T17:00:00Z"):
    return Signal(
        ref="SH-0001",
        date=date,
        origine="PAIEMENT",
        service="paiement",
        env="production",
        categorie="JOURNAL",
        gravite="MAJEUR",
        texte="timeout passerelle apres 30s",
    )


class TestAnalyse(unittest.TestCase):
    def test_repete(self):
        vus = set()

        # Première réception : pas un doublon.
        self.assertFalse(est_repete(sig(), vus))

        # Même signal reçu à nouveau : doublon.
        self.assertTrue(est_repete(sig(), vus))

    def test_dates_differentes(self):
        vus = set()

        self.assertFalse(est_repete(sig(), vus))

        # Même erreur une seconde plus tard : nouvel incident.
        self.assertFalse(
            est_repete(sig(date="2026-11-27T17:00:01Z"), vus)
        )


if __name__ == "__main__":
    unittest.main()