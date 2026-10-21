
import unittest

from src.contrat import Diagnostic, Signal
from src.notification import choisir_canal, composer, diffuser

def exemple(critique=True, niveau="BLOQUANT"):
    sig = Signal(
        "SH-0125",
        "2026-11-27T17:02:11Z",
        "PAIEMENT",
        "paiement",
        "production",
        "JOURNAL",
        "MAJEUR",
        "timeout passerelle apres 30s",
    )

    diag = Diagnostic(
        "SH-0125",
        niveau,
        "Passerelle lente",
        "Isoler le service paiement",
        critique,
        ["PAIEMENT"],
    )

    return sig, diag


class TestNotification(unittest.TestCase):

    def test_canaux(self):
        self.assertEqual(choisir_canal("BLOQUANT"), "SLACK")
        self.assertEqual(choisir_canal("MAJEUR"), "TEAMS")
        self.assertEqual(choisir_canal("MODERE"), "EMAIL")
        self.assertEqual(choisir_canal("MINEUR"), "TABLEAU")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")
    
    
    def test_composer(self):
        sig, diag = exemple()

        attendu = (
            "*** BLOQUANT *** Service : paiement\n"
            "Constat : timeout passerelle apres 30s\n"
            "Cause : Passerelle lente\n"
            "A faire : Isoler le service paiement\n"
            "Origines : PAIEMENT"
        )

        self.assertEqual(composer(sig, diag), attendu)
        self.assertEqual(len(composer(sig, diag).split("\n")), 5)
    
    
    def test_diffuser(self):
        sig, diag = exemple()
        registre = []

        msg = diffuser(sig, diag, registre)

        self.assertEqual(msg.signal_ref, "SH-0125")
        self.assertEqual(msg.canal, "SLACK")
        self.assertEqual(msg.destinataire, "astreinte-shop")
        self.assertEqual(msg.contenu, composer(sig, diag))
        self.assertEqual(registre, [msg])
        self.assertEqual(sig.etat, "DIFFUSE")



if __name__ == "__main__":
    unittest.main()
