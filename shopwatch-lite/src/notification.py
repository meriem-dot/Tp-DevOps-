
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
    msg = Message(
        signal_ref=sig.ref,
        canal=choisir_canal(diag.niveau),
        destinataire="astreinte-shop",
        contenu=composer(sig, diag),
    )

    registre.append(msg)
    sig.etat = "DIFFUSE"

    return msg



def approuver(diag: Diagnostic, reponse: str) -> bool:
    if not diag.critique:
        return True

    reponse_normalisee = "".join(reponse.split()).lower()
    return reponse_normalisee in {"o", "oui", "ok", "yes"}




def consigner(
    diag: Diagnostic,
    accord: bool,
    responsable: str,
    carnet: list,
    instant: str,
) -> dict:
    entree = {
        "ref": diag.signal_ref,
        "action": diag.action,
        "accord": accord,
        "responsable": responsable,
        "instant": instant,
    }

    carnet.append(entree)
    return entree

