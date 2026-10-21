import unittest

from src.analyse import est_repete
from src.contrat import Signal
from src.analyse import est_repete, compter_incidents
from src.analyse import chercher_fiches

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
    def test_compter_incidents(self):
        compteur = {}

        self.assertEqual(compter_incidents(sig(), compteur), 1)
        self.assertEqual(compter_incidents(sig(), compteur), 2)

        signal = sig()
        signal.gravite = "BLOQUANT"
        self.assertEqual(compter_incidents(signal, compteur), 3)

    def test_compter_par_service(self):
        compteur = {}
        compter_incidents(sig(), compteur)

        signal = sig()
        signal.service = "panier"

        self.assertEqual(compter_incidents(signal, compteur), 1)
        self.assertEqual(compteur, {"paiement": 1, "panier": 1})

    def test_ignorer_autres_signaux(self):
        compteur = {"paiement": 2}

        for niveau in ("MINEUR", "MODERE"):
            signal = sig()
            signal.gravite = niveau
            self.assertEqual(compter_incidents(signal, compteur), 0)

        for categorie in ("FAILLE", "BUILD_ECHEC", "BUILD_OK"):
            signal = sig()
            signal.categorie = categorie
            self.assertEqual(compter_incidents(signal, compteur), 0)

        self.assertEqual(compteur, {"paiement": 2})
    def test_chercher_fiches_ignore_casse(self):
        signal = sig()
        signal.texte = "TIMEOUT passerelle"
        base = {"timeout": "Verifier la passerelle"}

        self.assertEqual(
            chercher_fiches(signal, base),
            ["Verifier la passerelle"],
        )

    def test_chercher_plusieurs_fiches(self):
        signal = sig()
        signal.texte = "BUILD interrompu apres un TIMEOUT"
        base = {
            "timeout": "Conseil timeout",
            "build": "Conseil build",
        }

        self.assertEqual(
            chercher_fiches(signal, base),
            ["Conseil timeout", "Conseil build"],
        )

    def test_chercher_fiches_sans_resultat(self):
        signal = sig()
        signal.texte = "Service demarre"
        base = {"timeout": "Verifier la passerelle"}

        self.assertEqual(chercher_fiches(signal, base), [])
if __name__ == "__main__":
    unittest.main()
    