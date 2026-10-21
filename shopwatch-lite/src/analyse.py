from src.contrat import Diagnostic, Signal


def est_repete(sig: Signal, vus: set) -> bool:
    cle = (
        sig.date,
        sig.origine,
        sig.service,
        sig.categorie,
        sig.texte,
    )

    if cle in vus:
        return True

    vus.add(cle)
    return False