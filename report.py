
# **************************************************************************
# report.py : transforme les constats en rapport lisible.
# **************************************************************************

from __future__ import annotations

from models import AuditFinding, AuditResult, FindingSeverity


def group_findings(findings: list[AuditFinding], severity: FindingSeverity) -> list[AuditFinding]:
    return [f for f in findings if f.severity == severity]


def format_finding(finding: AuditFinding) -> str:
    return (
        f"[{finding.article_id}] {finding.title}\n"
        f"- Description : {finding.description}\n"
        f"- Justification : {finding.justification}"
    )


def build_report(result: AuditResult) -> str:
    """
    Construit le rapport final en texte.
    """
    blocking = group_findings(result.findings, FindingSeverity.BLOQUANT)
    major = group_findings(result.findings, FindingSeverity.MAJEUR)
    ambiguous = group_findings(result.findings, FindingSeverity.AMBIGU)
    conform = group_findings(result.findings, FindingSeverity.CONFORME)
    non_applicable = group_findings(result.findings, FindingSeverity.NON_APPLICABLE)

    lines: list[str] = []

    lines.append(f"RAPPORT D'AUDIT - {result.reference}")
    lines.append(f"Statut : {result.final_status}")
    lines.append(
        f"BLOQUANT : {result.blocking_count} | "
        f"MAJEUR : {result.major_count} | "
        f"AMBIGU : {result.ambiguous_count} | "
        f"CONFORME : {result.conform_count} | "
        f"NON APPLICABLE : {result.non_applicable_count}"
    )
    lines.append("")
    lines.append("RESUME EXECUTIF")
    lines.append(
        "La machine presente plusieurs points conformes, mais aussi des non-conformites "
        "documentaires et de couverture des exigences reglementaires qui conduisent a une "
        "conclusion globale de non-conformite."
    )
    lines.append("")

    if blocking:
        lines.append("ECARTS BLOQUANTS")
        for item in blocking:
            lines.append(format_finding(item))
            lines.append("")

    if major:
        lines.append("ECARTS MAJEURS")
        for item in major:
            lines.append(format_finding(item))
            lines.append("")

    if ambiguous:
        lines.append("CAS AMBIGUS")
        for item in ambiguous:
            lines.append(format_finding(item))
            lines.append("")

    if conform:
        lines.append("POINTS CONFORMES")
        for item in conform:
            lines.append(format_finding(item))
            lines.append("")

    if non_applicable:
        lines.append("EXIGENCES NON APPLICABLES")
        for item in non_applicable:
            lines.append(format_finding(item))
            lines.append("")

    return "\n".join(lines).strip()