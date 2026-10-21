
from src.contrat import Diagnostic, Message, Signal


def choisir_canal(niveau: str) -> str:
    canaux = {
        "BLOQUANT": "SLACK",
        "MAJEUR": "TEAMS",
        "MODERE": "EMAIL",
        "MINEUR": "TABLEAU",
    }

    if niveau not in canaux:
        raise ValueError(f"Niveau inconnu : {niveau}")

    return canaux[niveau]



def composer(sig: Signal, diag: Diagnostic) -> str:
    origines = " + ".join(diag.origines)

    return (
        f"*** {diag.niveau} *** Service : {sig.service}\n"
        f"Constat : {sig.texte}\n"
        f"Cause : {diag.cause}\n"
        f"A faire : {diag.action}\n"
        f"Origines : {origines}"
    )



def diffuser(sig: Signal, diag: Diagnostic, registre: list) -> Message:
    raise NotImplementedError


def approuver(diag: Diagnostic, reponse: str) -> bool:
    raise NotImplementedError


def consigner(
    diag: Diagnostic,
    accord: bool,
    responsable: str,
    carnet: list,
    instant: str,
) -> dict:
    raise NotImplementedError
