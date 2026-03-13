from analyzer import load_text as load_product_text
from analyzer import parse_product_sheet
from comparator import compare_requirements
from extractor import extract_requirements
from extractor import load_text as load_directive_text
from models import FindingSeverity
from report import build_report


def test_extract_requirements():
    reqs = extract_requirements(load_directive_text("data/directive.txt"))
    assert len(reqs) >= 10
    assert any(r.article_id == "Art.4.2" for r in reqs)
    assert any(r.article_id == "Art.9.1" and r.nature.value == "CONDITIONNELLE" for r in reqs)


def test_parse_product_sheet():
    facts = parse_product_sheet(load_product_text("data/product_sheet.txt"))
    assert facts.reference == "TX-900-CE-2024"
    assert "France" in facts.target_markets
    assert facts.admin_notes.get("Schemas des circuits de commande CN") is not None


def test_compare_requirements():
    reqs = extract_requirements(load_directive_text("data/directive.txt"))
    facts = parse_product_sheet(load_product_text("data/product_sheet.txt"))
    findings = compare_requirements(reqs, facts)

    art_42 = next(f for f in findings if f.article_id == "Art.4.2")
    art_71 = next(f for f in findings if f.article_id == "Art.7.1")
    art_81 = next(f for f in findings if f.article_id == "Art.8.1")
    art_91 = next(f for f in findings if f.article_id == "Art.9.1")

    assert art_42.severity == FindingSeverity.BLOQUANT
    assert art_71.severity == FindingSeverity.MAJEUR
    assert art_81.severity == FindingSeverity.MAJEUR
    assert art_91.severity == FindingSeverity.NON_APPLICABLE


def test_build_report():
    reqs = extract_requirements(load_directive_text("data/directive.txt"))
    facts = parse_product_sheet(load_product_text("data/product_sheet.txt"))
    findings = compare_requirements(reqs, facts)
    report = build_report(type("Dummy", (), {
        "reference": facts.reference,
        "findings": findings,
        "final_status": "NON CONFORME",
        "blocking_count": sum(1 for f in findings if f.severity == FindingSeverity.BLOQUANT),
        "major_count": sum(1 for f in findings if f.severity == FindingSeverity.MAJEUR),
        "ambiguous_count": sum(1 for f in findings if f.severity == FindingSeverity.AMBIGU),
        "conform_count": sum(1 for f in findings if f.severity == FindingSeverity.CONFORME),
        "non_applicable_count": sum(1 for f in findings if f.severity == FindingSeverity.NON_APPLICABLE),
    })())

    assert "RAPPORT D'AUDIT" in report
    assert "TX-900-CE-2024" in report
    assert "ECARTS BLOQUANTS" in report
