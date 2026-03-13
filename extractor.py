
from __future__ import annotations

import re
from pathlib import Path

from models import Requirement, RequirementNature


def load_text(path: str | Path) -> str:
    """
    Charge un fichier texte et retourne son contenu.
    """
    return Path(path).read_text(encoding="utf-8")

def clean_text(text: str) -> str:
    """
    Nettoyage léger :
    - normalise les fins de ligne,
    - retire les espaces inutiles.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def split_articles(directive_text: str) -> list[tuple[str, str, str]]:
    """
    Découpe la directive en articles.

    Retourne une liste de tuples :
    (article_id, titre, contenu_article)

    Par exemple :
    ("Art.4.2", "Dossier technique", "Le dossier technique doit comprendre ...")
    """
    pattern = r"(Art\.\d+\.\d+)\s*-\s*(.+?)\n(.*?)(?=(?:\nArt\.\d+\.\d+\s*-)|\Z)"
    matches = re.findall(pattern, directive_text, flags=re.DOTALL)

    articles = []
    for article_id, title, body in matches:
        articles.append((article_id.strip(), title.strip(), body.strip()))
    return articles

def infer_category(title: str) -> str:
    """
    Déduit une catégorie métier à partir du titre d'article.
    """
    lower_title = title.lower()

    if "dossier technique" in lower_title:
        return "DOCUMENTATION"
    if "marquage" in lower_title or "declaration" in lower_title:
        return "CONFORMITE"
    if "notice" in lower_title:
        return "NOTICE"
    if "securite" in lower_title or "protection" in lower_title or "arret d'urgence" in lower_title:
        return "SECURITE"
    if "risques" in lower_title:
        return "RISQUES"
    if "organismes notifies" in lower_title:
        return "CONFORMITE_CONDITIONNELLE"

    return "AUTRE"


def infer_nature(article_id: str, title: str, body: str) -> tuple[RequirementNature, str | None]:
    """
    Détermine si l'exigence est absolue ou conditionnelle.

    En effet, certaines exigences ne s'appliquent que sous conditions. 
    C'est le cas de l'Art.9.1.
    """
    text = f"{title} {body}".lower()

    if "pour les machines classees a risque eleve" in text or article_id == "Art.9.1":
        return RequirementNature.CONDITIONNELLE, "Applicable uniquement aux machines classees a risque eleve (categorie III ou IV)."

    return RequirementNature.ABSOLUE, None

def build_short_text(article_id: str, title: str, body: str) -> str:
    """
    Fabrique un résumé court et lisible de l'exigence.
    """
    lower_title = title.lower()
    compact_body = " ".join(body.split())