# Génération de rapport d'audit réglementaire

Ce projet réalise un audit automatisé de conformité réglementaire à partir de deux sources texte :

- une directive machines simplifiée ;
- une fiche produit décrivant une machine-outil CNC.

L'objectif est de :

1. extraire les exigences réglementaires ;
2. parser les informations de la fiche produit ;
3. comparer les exigences aux faits identifiés ;
4. produire un rapport d'audit lisible avec classification des écarts.

## Structure du projet

```text
.
├── audit.py
├── analyzer.py
├── comparator.py
├── extractor.py
├── models.py
├── report.py
├── requirements.txt
├── README.md
├── DECISIONS.md
├── data/
│   ├── directive.txt
│   └── product_sheet.txt
└── tests/
    ├── conftest.py
    └── test_smoke.py