
# ******************************************************************************
# analyzer.py : parse la fiche produit.
# ******************************************************************************

from __future__ import annotations

import re
from pathlib import Path

from models import ProductInfos

def load_text(path: str | Path) -> str:
    """
    Charge un fichier texte.
    """
    return Path(path).read_text(encoding="utf-8")


def clean_text(text: str) -> str:
    """
    Nettoyage léger.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def parse_simple_field(text: str, field_name: str) -> str | None:
    """
    Extrait un champ simple sous forme :
    'Champ : valeur'
    """
    pattern = rf"{re.escape(field_name)}\s*:\s*(.+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None


def parse_target_markets(value: str | None) -> list[str]:
    """
    Convertit 'France, Allemagne, Espagne' -> ['France', 'Allemagne', 'Espagne']
    """
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

def extract_section(text: str, section_name: str) -> str:
    """
    Extrait le contenu d'une section délimitée par :
    --- NOM SECTION ---
    """
    pattern = rf"--- {re.escape(section_name)} ---\n(.*?)(?=(?:\n--- [A-ZÉÈA-Z ]+ ---)|\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""

def parse_section_as_dict(section_text: str) -> dict[str, str]:
    """
    Parse une section sous forme de lignes 'clé : valeur'.
    Gère aussi les valeurs sur plusieurs lignes.
    """
    result: dict[str, str] = {}

    current_key = None
    current_value_parts: list[str] = []

    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" in line:
            if current_key is not None:
                result[current_key] = " ".join(current_value_parts).strip()

            key, value = line.split(":", 1)
            current_key = key.strip()
            current_value_parts = [value.strip()]
        else:
            if current_key is not None:
                current_value_parts.append(line)

    if current_key is not None:
        result[current_key] = " ".join(current_value_parts).strip()

    return result

def parse_product_sheet(product_text: str) -> ProductInfos:
    """
    Parse la fiche produit et la convertit en objet ProductInfos.
    """
    text = clean_text(product_text)

    facts = ProductInfos(
        manufacturer=parse_simple_field(text, "Fabricant"),
        address=parse_simple_field(text, "Adresse"),
        signatory=parse_simple_field(text, "Signataire"),
        reference=parse_simple_field(text, "Reference"),
        destination=parse_simple_field(text, "Destination"),
        target_markets=parse_target_markets(parse_simple_field(text, "Marches vises")),
    )

    documentation_text = extract_section(text, "DOCUMENTATION")
    safety_text = extract_section(text, "SECURITE")
    conformity_text = extract_section(text, "MARQUAGE ET CONFORMITE")
    user_docs_text = extract_section(text, "DOCUMENTATION UTILISATEUR")
    admin_notes_text = extract_section(text, "NOTE ADMINISTRATIVE")

    facts.documentation = parse_section_as_dict(documentation_text)
    facts.safety = parse_section_as_dict(safety_text)
    facts.conformity = parse_section_as_dict(conformity_text)
    facts.user_docs = parse_section_as_dict(user_docs_text)
    facts.admin_notes = parse_section_as_dict(admin_notes_text)

    return facts

if __name__ == "__main__":
    text = load_text("data/product_sheet.txt")
    facts = parse_product_sheet(text)

    print("REFERENCE:", facts.reference)
    print("FABRICANT:", facts.manufacturer)
    print("MARCHES:", facts.target_markets)
    print("\nDOCUMENTATION:")
    for k, v in facts.documentation.items():
        print(f"- {k}: {v}")

    print("\nSECURITE:")
    for k, v in facts.safety.items():
        print(f"- {k}: {v}")

    print("\nCONFORMITE:")
    for k, v in facts.conformity.items():
        print(f"- {k}: {v}")

    print("\nUSER DOCS:")
    for k, v in facts.user_docs.items():
        print(f"- {k}: {v}")

    print("\nADMIN NOTES:")
    for k, v in facts.admin_notes.items():
        print(f"- {k}: {v}")