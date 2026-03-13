
# *****************************************************************************
# audit.py : script principal en une commande et retournant un rapport complet.
# *****************************************************************************

from __future__ import annotations

from analyzer import load_text as load_product_text
from analyzer import parse_product_sheet
from comparator import compare_requirements
from extractor import extract_requirements
from extractor import load_text as load_directive_text
from models import AuditResult
from report import build_report


DIRECTIVE_PATH = "data/directive.txt"
PRODUCT_SHEET_PATH = "data/product_sheet.txt"


def main() -> None:
    """
    Orchestration complète de l'audit :
    1. lecture des sources,
    2. extraction des exigences,
    3. analyse de la fiche produit,
    4. comparaison,
    5. génération du rapport final.
    """
    directive_text = load_directive_text(DIRECTIVE_PATH)
    product_text = load_product_text(PRODUCT_SHEET_PATH)

    requirements = extract_requirements(directive_text)
    product_facts = parse_product_sheet(product_text)
    findings = compare_requirements(requirements, product_facts)

    result = AuditResult(
        reference=product_facts.reference or "UNKNOWN_REFERENCE",
        findings=findings,
    )

    report = build_report(result)
    print(report)


if __name__ == "__main__":
    main()