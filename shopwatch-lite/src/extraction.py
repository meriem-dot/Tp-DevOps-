
import re
from src.contrat import Signal


def masquer_donnees(texte: str) -> str:
    # Masquer les mots de passe
    texte = re.sub(
        r"(?i)\b(pwd|password|token|secret)=\S+",
        lambda m: m.group(1) + "=[MASQUE]",
        texte
    )

    # Masquer les numeros de carte bancaire
    texte = re.sub(
        r"\b\d{13,19}\b",
        "[MASQUE]",
        texte
    )

    return texte