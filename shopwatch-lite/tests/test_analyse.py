import unittest

from src.analyse import (
    est_repete,
    compter_incidents,
    chercher_fiches,
    evaluer,
    diagnostiquer,
)
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

        self.assertFalse(est_repete(sig(), vus))
        self.assertTrue(est_repete(sig(), vus))

    def test_dates_differentes(self):
        vus = set()

        self.assertFalse(est_repete(sig(), vus))
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

    def test_evaluer_panne_en_boucle(self):
        signal = sig()

        self.assertEqual(evaluer(signal, 3), "MAJEUR")
        self.assertEqual(evaluer(signal, 4), "BLOQUANT")
        self.assertEqual(evaluer(signal, 5), "BLOQUANT")

    def test_evaluer_conserve_gravite(self):
        for niveau in ("MINEUR", "MODERE", "MAJEUR", "BLOQUANT"):
            signal = sig()
            signal.gravite = niveau

            with self.subTest(niveau=niveau):
                self.assertEqual(evaluer(signal), niveau)

    def test_diagnostic_bloquant(self):
        signal = sig()
        base = {"timeout": "Verifier la passerelle"}

        diagnostic = diagnostiquer(signal, base, 4)

        self.assertEqual(diagnostic.signal_ref, signal.ref)
        self.assertEqual(diagnostic.niveau, "BLOQUANT")
        self.assertEqual(diagnostic.cause, "Verifier la passerelle")
        self.assertEqual(diagnostic.action, "Isoler le service paiement")
        self.assertTrue(diagnostic.critique)
        self.assertEqual(diagnostic.origines, ["PAIEMENT"])
        self.assertEqual(signal.etat, "EVALUE")

    def test_diagnostic_sans_conseil(self):
        diagnostic = diagnostiquer(sig(), {})

        self.assertEqual(
            diagnostic.cause,
            "Cause inconnue : verification manuelle",
        )
        self.assertEqual(diagnostic.action, "Observer")
        self.assertFalse(diagnostic.critique)

    def test_diagnostic_joint_conseils(self):
        signal = sig()
        signal.texte = "timeout pendant le build"
        base = {
            "timeout": "Conseil timeout",
            "build": "Conseil build",
        }

        diagnostic = diagnostiquer(signal, base)

        self.assertEqual(
            diagnostic.cause,
            "Conseil timeout ; Conseil build",
        )

    def test_diagnostic_faille_prioritaire(self):
        signal = sig()
        signal.categorie = "FAILLE"
        signal.gravite = "BLOQUANT"
        signal.service = "panier"

        diagnostic = diagnostiquer(signal, {})

        self.assertEqual(
            diagnostic.action,
            "Corriger la dependance panier",
        )
        self.assertFalse(diagnostic.critique)

    def test_diagnostic_build_prioritaire(self):
        signal = sig()
        signal.categorie = "BUILD_ECHEC"
        signal.service = "tests"

        diagnostic = diagnostiquer(signal, {}, 4)

        self.assertEqual(diagnostic.niveau, "BLOQUANT")
        self.assertEqual(diagnostic.action, "Rejouer le build tests")
        self.assertFalse(diagnostic.critique)


if __name__ == "__main__":
    unittest.main()