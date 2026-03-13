
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

    if article_id == "Art.4.2":
        return "Le dossier technique doit inclure description generale, schemas, notes de calcul, normes appliquees et declaration CE."
    if article_id == "Art.5.1":
        return "La machine mise sur le marche dans l'UE doit porter le marquage CE."
    if article_id == "Art.5.2":
        return "La declaration CE doit contenir les mentions obligatoires et etre signee par un representant habilite."
    if article_id == "Art.6.1":
        return "Les elements mobiles dangereux doivent etre proteges par des dispositifs non contournables et sans risque additionnel."
    if article_id == "Art.6.2":
        return "La machine doit disposer d'un arret d'urgence identifiable, accessible et conforme EN 13850."
    if article_id == "Art.7.1":
        return "La notice doit etre fournie dans les langues officielles des marches vises ainsi que dans la langue d'origine du fabricant."
    if article_id == "Art.7.2":
        return "La notice doit inclure fabricant, designation machine, mise en service, utilisation, maintenance et risques residuels."
    if article_id == "Art.8.1":
        return "L'evaluation des risques doit couvrir l'ensemble du cycle de vie de la machine et etre documentee."
    if article_id == "Art.8.2":
        return "La reduction des risques doit suivre l'ordre : conception, protection, information sur les risques residuels."
    if article_id == "Art.9.1":
        return "Un organisme notifie et un certificat CE de type sont obligatoires pour les machines categorie III ou IV."

    first_sentence = compact_body.split(".")[0].strip()
    return first_sentence if first_sentence else compact_body[:120]

def extract_requirements(directive_text: str) -> list[Requirement]:
    """
    Parse la directive et retourne une liste structurée d'exigences.
    """
    directive_text = clean_text(directive_text)
    articles = split_articles(directive_text)

    requirements: list[Requirement] = []

    for article_id, title, body in articles:
        nature, condition = infer_nature(article_id, title, body)

        requirement = Requirement(
            article_id=article_id,
            title=title,
            short_text=build_short_text(article_id, title, body),
            category=infer_category(title),
            nature=nature,
            source_text=body,
            condition=condition,
        )
        requirements.append(requirement)

    return requirements

if __name__ == "__main__":
    text = load_text("data/directive.txt")
    requirements = extract_requirements(text)

    for req in requirements:
        print(f"{req.article_id} | {req.title} | {req.category} | {req.nature}")
        print(f"  -> {req.short_text}")
        if req.condition:
            print(f"  condition: {req.condition}")