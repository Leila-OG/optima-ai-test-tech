
# ***********************************************************************************
# comparator.py : compare les exigences et les faits, puis sort des constats d’audit.
# On va faire une logique par article.
# ***********************************************************************************

from __future__ import annotations

from models import (
    AuditFinding,
    FindingSeverity,
    ProductInfos,
    Requirement,
)


def normalize(value: str | None) -> str:
    """
    Normalise légèrement une chaîne pour des comparaisons simples.
    """
    return (value or "").strip().lower()


def contains_any(value: str | None, terms: list[str]) -> bool:
    """
    Vérifie si l'une des expressions est présente.
    """
    normalized = normalize(value)
    return any(term.lower() in normalized for term in terms)

def check_art_4_1(req: Requirement, facts: ProductInfos) -> AuditFinding:
    """
    Sécurité générale.
    La fiche ne permet pas de démontrer complètement l'absence de tout risque
    sur installation + maintenance + utilisation. On préfère rester prudent et classer en AMBIGU.
    """
    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.AMBIGU,
        description="La securite generale de la machine n'est pas demontree de facon exhaustive.",
        justification=(
            "La fiche produit apporte plusieurs indices favorables (capots de protection, arret d'urgence, "
            "reduction des risques par conception), mais elle ne permet pas d'etablir explicitement "
            "que la machine ne presente aucun risque lors de l'installation, de la maintenance et de l'utilisation "
            "conformement a sa destination."
        ),
    )

def check_art_4_2(req: Requirement, facts: ProductInfos) -> AuditFinding:
    """
    Dossier technique.
    Le sujet fait apparaitre un point contradictoire :
    - dossier technique : COMPLET
    - mais schémas des circuits de commande CN : EN COURS DE FINALISATION
    """
    admin_note = facts.admin_notes.get("Schemas des circuits de commande CN", "")
    description = facts.documentation.get("Description generale", "")
    notes = facts.documentation.get("Notes de calcul mecaniques", "")
    norms = facts.documentation.get("Liste des normes appliquees", "")
    ce_decl = facts.documentation.get("Declaration CE", "")

    missing_core_items = []
    if not description:
        missing_core_items.append("description generale")
    if not notes:
        missing_core_items.append("notes de calcul")
    if not norms:
        missing_core_items.append("liste des normes appliquees")
    if not ce_decl:
        missing_core_items.append("declaration CE")

    if contains_any(admin_note, ["en cours de finalisation"]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.BLOQUANT,
            description="Les schemas des circuits de commande ne sont pas finalises.",
            justification=(
                "L'article 4.2 impose que le dossier technique comprenne les schemas des circuits de commande. "
                "Or la note administrative indique explicitement que les schemas des circuits de commande CN sont "
                "encore en cours de finalisation, ce qui contredit le caractere complet du dossier technique."
            ),
        )

    if missing_core_items:
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.MAJEUR,
            description="Le dossier technique semble incomplet.",
            justification=(
                f"Les elements suivants ne sont pas retrouves clairement dans la fiche produit : {', '.join(missing_core_items)}."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.CONFORME,
        description="Le dossier technique parait documente avec les elements principaux attendus.",
        justification=(
            "La fiche mentionne une description generale, des notes de calcul, une liste de normes appliquees "
            "et une declaration CE. Aucun manque explicite n'est releve hors contradiction documentaire."
        ),
    )

def check_art_5_1(req: Requirement, facts: ProductInfos) -> AuditFinding:
    ce_mark = facts.conformity.get("Marquage CE appose sur la machine", "")
    if contains_any(ce_mark, ["oui"]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.CONFORME,
            description="Le marquage CE est indique comme appose sur la machine.",
            justification="La fiche produit mentionne explicitement : 'Marquage CE appose sur la machine : OUI'.",
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.BLOQUANT,
        description="Le marquage CE n'est pas etabli.",
        justification="Le marquage CE est obligatoire avant mise sur le marche dans l'Union Europeenne.",
    )

def check_art_5_2(req: Requirement, facts: ProductFacts) -> AuditFinding:
    ce_decl = facts.documentation.get("Declaration CE", "")
    has_signature = contains_any(ce_decl, ["signee"])
    has_name = bool(facts.manufacturer)
    has_address = bool(facts.address)
    has_description = bool(facts.destination)

    if has_signature and has_name and has_address and has_description:
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.AMBIGU,
            description="La declaration CE semble signee mais son contenu detaille n'est pas entierement verifiable.",
            justification=(
                "La fiche confirme une declaration CE signee par un representant habilite, et les informations "
                "sur fabricant, adresse et description machine existent dans la fiche. En revanche, il n'est pas "
                "explicitement etabli que toutes ces mentions figurent bien dans la declaration elle-meme, ni que "
                "les directives appliquees y sont reprises."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.MAJEUR,
        description="La declaration CE semble incomplète ou insuffisamment justifiee.",
        justification=(
            "L'article 5.2 exige des mentions obligatoires et une signature habilitee. "
            "Les informations disponibles ne permettent pas de verifier toutes ces mentions."
        ),
    )

def check_art_6_1(req: Requirement, facts: ProductInfos) -> AuditFinding:
    protection = facts.safety.get("Capots de protection sur broche et zone d'usinage", "")

    if contains_any(protection, ["oui", "verrouilles"]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.CONFORME,
            description="Les elements mobiles dangereux semblent proteges.",
            justification=(
                "La fiche mentionne des capots de protection sur la broche et la zone d'usinage, avec verrouillage. "
                "Cela repond de facon credible a l'exigence de protection des elements mobiles."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.MAJEUR,
        description="La protection des elements mobiles n'est pas suffisamment etablie.",
        justification="Aucun dispositif de protection adequat n'est clairement retrouve dans la fiche.",
    )

def check_art_6_2(req: Requirement, facts: ProductFacts) -> AuditFinding:
    emergency = facts.safety.get("Dispositif de coupure d'urgence", "")
    certification = facts.safety.get("Certification arret urgence", "")

    if contains_any(emergency, ["oui"]) and contains_any(certification, ["13850"]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.CONFORME,
            description="La machine dispose d'un arret d'urgence documente et reference a la norme 13850.",
            justification=(
                "La fiche mentionne un dispositif de coupure d'urgence present, localise en facade et au pupitre, "
                "ainsi qu'une conformite a EN ISO 13850. Le sujet demandait EN 13850 ; la correspondance terminologique "
                "autour de 13850 est acceptee ici comme satisfaisante."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.MAJEUR,
        description="L'arret d'urgence n'est pas suffisamment etabli.",
        justification="La fiche ne permet pas de verifier clairement la presence et la conformite de l'arret d'urgence.",
    )

def check_art_7_1(req: Requirement, facts: ProductInfos) -> AuditFinding:
    notice = facts.user_docs.get("Notice d'instructions", "")
    origin_notice = facts.admin_notes.get("Version notice langue d'origine (anglais)", "")
    markets = facts.target_markets

    missing_languages = []

    market_to_language = {
        "France": "francais",
        "Allemagne": "allemand",
        "Espagne": "espagnol",
    }

    notice_norm = normalize(notice)
    for market in markets:
        expected_language = market_to_language.get(market)
        if expected_language and expected_language not in notice_norm:
            missing_languages.append(expected_language)

    missing_origin = contains_any(origin_notice, ["non incluse"])

    if missing_languages or missing_origin:
        reasons = []
        if missing_languages:
            reasons.append(f"langues officielles manquantes pour les marches vises : {', '.join(missing_languages)}")
        if missing_origin:
            reasons.append("version dans la langue d'origine du fabricant absente")

        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.MAJEUR,
            description="La notice n'est pas disponible dans toutes les langues requises.",
            justification=(
                "L'article 7.1 impose la langue officielle de chaque Etat membre vise et la langue d'origine du fabricant. "
                + " ; ".join(reasons) + "."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.CONFORME,
        description="La notice semble fournie dans les langues requises.",
        justification="Les langues de mise sur le marche et la langue d'origine paraissent couvertes.",
    )

def check_art_7_2(req: Requirement, facts: ProductInfos) -> AuditFinding:
    has_manufacturer = bool(facts.manufacturer)
    has_machine_designation = bool(facts.reference) or bool(facts.destination)
    has_commissioning = contains_any(facts.user_docs.get("Contenu notice - mise en service", ""), ["oui"])
    has_use = contains_any(facts.user_docs.get("Contenu notice - utilisation", ""), ["oui"])
    has_maintenance = contains_any(facts.user_docs.get("Contenu notice - maintenance", ""), ["oui"])
    has_residual_risks = contains_any(facts.user_docs.get("Contenu notice - risques residuels", ""), ["oui"])

    if all([has_manufacturer, has_machine_designation, has_commissioning, has_use, has_maintenance, has_residual_risks]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.CONFORME,
            description="Le contenu principal de la notice est present.",
            justification=(
                "La fiche mentionne les rubriques de mise en service, utilisation, maintenance et risques residuels. "
                "Les informations d'identification du fabricant et de la machine existent egalement dans la fiche."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.AMBIGU,
        description="Le contenu detaille de la notice n'est pas totalement verifiable.",
        justification="Certaines rubriques attendues ne sont pas clairement retrouvees ou pas reliees explicitement a la notice.",
    )

def check_art_8_1(req: Requirement, facts: ProductInfos) -> AuditFinding:
    risk_eval = facts.safety.get("Evaluation des risques", "")

    if contains_any(risk_eval, ["phase d'utilisation"]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.MAJEUR,
            description="L'evaluation des risques ne couvre pas explicitement tout le cycle de vie.",
            justification=(
                "L'article 8.1 exige une evaluation couvrant l'ensemble du cycle de vie de la machine. "
                "Or la fiche mentionne seulement : 'REALISEE - phase d'utilisation'."
            ),
        )

    if risk_eval:
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.AMBIGU,
            description="Une evaluation des risques existe mais son perimetre exact n'est pas clair.",
            justification="La fiche mentionne une evaluation des risques sans preciser explicitement l'ensemble du cycle de vie.",
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.BLOQUANT,
        description="Aucune evaluation des risques n'est identifiee.",
        justification="L'evaluation des risques est une exigence structurante de la directive.",
    )

def check_art_8_2(req: Requirement, facts: ProductFacts) -> AuditFinding:
    design_reduction = facts.safety.get("Reduction des risques par conception", "")
    residual_risks_notice = facts.user_docs.get("Contenu notice - risques residuels", "")
    protection = facts.safety.get("Capots de protection sur broche et zone d'usinage", "")

    has_design = contains_any(design_reduction, ["oui"])
    has_protection = contains_any(protection, ["oui"])
    has_info = contains_any(residual_risks_notice, ["oui"])

    if has_design and has_protection and has_info:
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.CONFORME,
            description="Les trois niveaux de reduction des risques sont representes.",
            justification=(
                "La fiche fait apparaitre une reduction par conception, des mesures de protection physiques "
                "et une information sur les risques residuels dans la notice."
            ),
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.AMBIGU,
        description="L'ordre complet de reduction des risques n'est pas demontre clairement.",
        justification=(
            "Certaines briques sont presentes, mais la fiche ne documente pas necessairement l'ordre de priorite "
            "de facon explicite et exhaustive."
        ),
    )

def check_art_9_1(req: Requirement, facts: ProductInfos) -> AuditFinding:
    category = facts.conformity.get("Categorie machine", "")

    if contains_any(category, ["non classe categorie iii ou iv", "risque standard"]):
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.NON_APPLICABLE,
            description="L'exigence d'organisme notifie n'est pas applicable.",
            justification=(
                "L'article 9.1 ne s'applique qu'aux machines classees categorie III ou IV. "
                "La fiche indique une machine a risque standard, non classee categorie III ou IV."
            ),
        )

    notified_number = facts.conformity.get("Numero organisme notifie", "")
    ce_type = facts.conformity.get("Certificat examen CE de type", "")

    if notified_number and ce_type:
        return AuditFinding(
            article_id=req.article_id,
            title=req.title,
            severity=FindingSeverity.CONFORME,
            description="Les informations relatives a l'organisme notifie semblent presentes.",
            justification="La machine semble relever du dispositif avec organisme notifie et les pieces sont presentes.",
        )

    return AuditFinding(
        article_id=req.article_id,
        title=req.title,
        severity=FindingSeverity.BLOQUANT,
        description="Les informations d'organisme notifie manquent pour une machine potentiellement soumise a cette exigence.",
        justification=(
            "Si la machine etait classee III ou IV, le numero d'organisme notifie et le certificat CE de type "
            "seraient obligatoires avant mise sur le marche."
        ),
    )

def compare_requirements(requirements: list[Requirement], facts: ProductInfos) -> list[AuditFinding]:
    """
    Compare chaque exigence à la fiche produit.
    """
    findings: list[AuditFinding] = []

    dispatch = {
        "Art.4.1": check_art_4_1,
        "Art.4.2": check_art_4_2,
        "Art.5.1": check_art_5_1,
        "Art.5.2": check_art_5_2,
        "Art.6.1": check_art_6_1,
        "Art.6.2": check_art_6_2,
        "Art.7.1": check_art_7_1,
        "Art.7.2": check_art_7_2,
        "Art.8.1": check_art_8_1,
        "Art.8.2": check_art_8_2,
        "Art.9.1": check_art_9_1,
    }

    for req in requirements:
        checker = dispatch.get(req.article_id)
        if checker is None:
            findings.append(
                AuditFinding(
                    article_id=req.article_id,
                    title=req.title,
                    severity=FindingSeverity.AMBIGU,
                    description="Aucune regle de comparaison specifique n'a ete definie pour cet article.",
                    justification="Le moteur de comparaison actuel repose sur des regles explicites par article.",
                )
            )
            continue

        findings.append(checker(req, facts))

    return findings