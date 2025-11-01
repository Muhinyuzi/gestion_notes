# some_ai_module.py
from textwrap import shorten

def generate_summary(contenu: str) -> str:
    """
    Génère un résumé automatique du texte.
    Pour l'instant : version simplifiée sans IA (tronque le texte proprement)
    """
    if not contenu:
        return ""

    # Si tu veux faire un résumé plus "intelligent", tu pourras ici
    # utiliser un vrai modèle (HuggingFace, OpenAI, etc.)
    resume = shorten(contenu, width=200, placeholder="...")

    return f"Résumé automatique : {resume}"