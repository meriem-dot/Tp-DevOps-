
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


def lire_journal(
    ligne: str,
    numero: int,
    origine: str = "PAIEMENT",
    env: str = "production",
) -> Signal:

    match = re.search(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        ligne
    )

    if not match:
        raise ValueError("Date absente du journal")

    date = match.group().replace(" ", "T") + "Z"

    texte = ligne.upper()

    if "CRITICAL" in texte or "FATAL" in texte:
        gravite = "BLOQUANT"
    elif "ERROR" in texte:
        gravite = "MAJEUR"
    elif "WARNING" in texte or "WARN" in texte:
        gravite = "MODERE"
    else:
        gravite = "MINEUR"

    elements = ligne.split()
    service = elements[2] if len(elements) > 2 else "inconnu"

    return Signal(
        ref=f"SH-{numero:04d}",
        date=date,
        origine=origine,
        service=service,
        env=env,
        categorie="JOURNAL",
        gravite=gravite,
        texte=masquer_donnees(ligne),
        etat="RECU"
    )

def lire_scan(
    rapport: dict,
    numero: int,
    env: str = "production",
) -> Signal:

    return Signal(
        ref=f"SH-{numero:04d}",
        date=rapport.get("date", ""),
        origine="SCANNER",
        service=rapport.get("service", "inconnu"),
        env=env,
        categorie="FAILLE",
        gravite=rapport.get("gravite", "MAJEUR"),
        texte=masquer_donnees(rapport.get("texte", "")),
        etat="RECU"
    )


def lire_build(
    rapport: dict,
    numero: int,
    env: str = "production",
) -> Signal:

    statut = rapport.get("statut", "").upper()

    if statut == "OK":
        categorie = "BUILD_OK"
        gravite = "MINEUR"
    else:
        categorie = "BUILD_ECHEC"
        gravite = "MAJEUR"

    return Signal(
        ref=f"SH-{numero:04d}",
        date=rapport.get("date", ""),
        origine="BUILD",
        service=rapport.get("service", "inconnu"),
        env=env,
        categorie=categorie,
        gravite=gravite,
        texte=masquer_donnees(rapport.get("texte", "")),
        etat="RECU"
    )
