## 1. Objectif et approche retenue

L'objectif était de construire un pipeline Python simple, lisible et exécutable en une commande pour :

1. extraire les exigences d'une directive machines simplifiée ;
2. analyser une fiche produit ;
3. comparer les deux ;
4. produire un rapport d'audit argumenté.

J'ai choisi une approche **déterministe par règles métier**, sans LLM ni base de données. 

Cette décision a été prise pour plusieurs raisons :
- le périmètre est fermé et entièrement fourni dans l'énoncé ;
- la difficulté principale est la **précision de lecture**, pas l'apprentissage automatique ;
- un comportement déterministe facilite la justification des écarts ;
- l'absence de dépendance à une API externe rend la solution plus robuste et plus simple à exécuter ;
- le sujet valorise explicitement les choix justifiés et la documentation honnête des cas ambigus.

## 2. Pourquoi je n'ai pas utilisé de base de données

Je n'ai pas utilisé de base de données, car cela n'apportait pas de valeur sur ce test.

Les données sont limitées à deux textes fournis dans le sujet :

- la directive ;
- la fiche produit.

J'ai donc préféré les stocker dans deux fichiers :

- `data/directive.txt`
- `data/product_sheet.txt`

Cette solution est plus simple, plus lisible et plus adaptée à un test technique court.

## 3. Architecture choisie

J'ai séparé les responsabilités en plusieurs modules :

- `extractor.py` : extraction des exigences réglementaires ;
- `analyzer.py` : parsing de la fiche produit ;
- `comparator.py` : comparaison article par article ;
- `report.py` : génération du rapport final ;
- `audit.py` : orchestration de bout en bout ;
- `models.py` : structures de données partagées.

Cette séparation permet :

- un code plus lisible ;
- des tests plus simples ;
- une meilleure maintenabilité ;
- une logique explicite et traçable.

## 4. Structures de données

J'ai utilisé des dataclasses et des enums pour représenter :

- une exigence réglementaire ;
- les faits extraits de la fiche produit ;
- un constat d'audit ;
- le résultat global.

Ce choix améliore :

- la clarté du code ;
- le typage ;
- la cohérence entre modules ;
- la lisibilité des objets manipulés.

## 5. Logique d'extraction des exigences

L'extraction des exigences a été faite à partir des articles de la directive.

Pour chaque article, je reconstruis :

- un identifiant (`Art.x.x`) ;
- un titre ;
- un résumé court ;
- une catégorie métier ;
- une nature : `ABSOLUE` ou `CONDITIONNELLE`.

J'ai explicitement marqué l'article 9.1 comme **conditionnel**, car il ne s'applique qu'aux machines classées à risque élevé de catégorie III ou IV.

## 6. Logique d'analyse de la fiche produit

La fiche produit est parsée par sections :

- documentation ;
- sécurité ;
- marquage et conformité ;
- documentation utilisateur ;
- note administrative.

Chaque section est transformée en dictionnaire clé / valeur pour permettre ensuite une comparaison simple et explicite.

J'ai également extrait les métadonnées générales :

- fabricant ;
- adresse ;
- signataire ;
- référence ;
- destination ;
- marchés visés.

## 7. Logique de comparaison

La comparaison repose sur des fonctions métier explicites, une par article.

Exemples :

- `check_art_4_2`
- `check_art_7_1`
- `check_art_8_1`
- `check_art_9_1`

J'ai préféré cette approche à une comparaison plus implicite ou "magique", car :

- elle rend les décisions transparentes ;
- elle permet d'expliquer précisément chaque conclusion ;
- elle est adaptée à un petit corpus réglementaire ;
- elle facilite l'identification des cas ambigus.

## 8. Gestion des ambiguïtés

Le sujet insiste sur le fait que certains éléments sont volontairement ambigus ou incomplets. J'ai donc distingué plusieurs niveaux :

- `BLOQUANT`
- `MAJEUR`
- `AMBIGU`
- `CONFORME`
- `NON_APPLICABLE`

J'ai utilisé `AMBIGU` lorsque la fiche donne des indices favorables, mais pas assez pour conclure de manière certaine.

### Cas ambigus retenus

#### Art.4.1 - Sécurité générale

La fiche produit donne plusieurs signaux positifs :

- capots de protection ;
- arrêt d'urgence ;
- réduction des risques par conception.

Cependant, elle ne démontre pas explicitement que la machine est sûre sur l'ensemble du périmètre demandé par l'article : installation, entretien et utilisation conforme à la destination.

J'ai donc choisi `AMBIGU` plutôt que `CONFORME`.

#### Art.5.2 - Déclaration de conformité

La fiche indique qu'une déclaration CE est signée par un représentant habilité.

En revanche, il n'est pas possible de vérifier directement que la déclaration contient bien toutes les mentions obligatoires exigées par l'article 5.2.

J'ai donc choisi `AMBIGU` plutôt que `CONFORME`.

## 9. Principaux écarts identifiés

### Art.4.2 - Dossier technique -> BLOQUANT

La fiche indique :

- `Dossier technique : COMPLET`

mais la note administrative indique aussi :

- `Schémas des circuits de commande CN : EN COURS DE FINALISATION`

J'ai interprété cela comme une contradiction forte sur une pièce exigée du dossier technique.

J'ai donc classé ce point en `BLOQUANT`.

### Art.7.1 - Notice d'instructions -> MAJEUR

Les marchés visés sont :

- France
- Allemagne
- Espagne

La notice est indiquée comme présente en :

- français
- allemand

La version en espagnol manque donc pour un marché visé.

La note administrative précise également que la version dans la langue d'origine du fabricant (anglais) n'est pas incluse.

J'ai donc classé ce point en `MAJEUR`.

### Art.8.1 - Évaluation des risques -> MAJEUR

L'article demande une évaluation des risques couvrant l'ensemble du cycle de vie de la machine.

La fiche indique seulement :

- `REALISEE - phase d'utilisation`

J'ai donc considéré que le périmètre demandé n'était pas couvert explicitement, ce qui justifie un `MAJEUR`.

### Art.9.1 - Organismes notifiés -> NON_APPLICABLE

L'exigence ne s'applique qu'aux machines classées à risque élevé de catégorie III ou IV.

La fiche indique au contraire :

- `risque standard`
- `non classe categorie III ou IV`

J'ai donc explicitement traité ce point comme `NON_APPLICABLE` pour éviter un faux positif.

## 10. Cas de robustesse gérés

J'ai essayé de rendre la solution robuste sur les points suivants :

- champs présents mais partiels ;
- vocabulaire différent entre directive et fiche produit ;
- présence de formulations indirectes ;
- exigences conditionnelles ;
- informations administratives contradictoires ;
- absence d'API LLM.

### Exemple de robustesse sémantique légère

Pour l'article sur l'arrêt d'urgence, la directive mentionne `EN 13850` tandis que la fiche produit indique `EN ISO 13850`.

J'ai choisi de considérer cela comme suffisamment proche pour conclure à une conformité, au lieu de faire une comparaison textuelle stricte.

## 11. Ce qui m'a bloqué ou ralenti

Les principaux points délicats ont été :

- décider où placer la frontière entre `CONFORME` et `AMBIGU` ;
- interpréter les contradictions documentaires ;
- éviter de sur-conclure à partir d'indices partiels ;
- choisir un niveau de sévérité cohérent entre les articles ;
- gérer proprement les imports de tests avec `pytest`.

Concernant les tests, j'ai rencontré un problème de résolution d'import (`ModuleNotFoundError` sur `analyzer`) lors de l'exécution de `pytest`.

Je l'ai résolu en ajoutant un fichier `tests/conftest.py` pour injecter la racine du projet dans le `PYTHONPATH` pendant les tests.

Par ailleurs, respecter les 2h effectif pour réaliser ce test fût aussi un challenge pour moi.

## 12. Pourquoi je n'ai pas utilisé un LLM

Le sujet autorise l'absence d'API LLM à condition d'expliquer ce que cela aurait apporté.

Je n'ai pas utilisé de LLM pour les raisons suivantes :

- besoin de reproductibilité ;
- volonté d'avoir des règles métier explicites ;
- temps de test limité ;
- périmètre assez petit pour être couvert sans modèle génératif ;
- risque d'hallucination ou de justification moins traçable.

## 13. Ce qu'un LLM aurait pu apporter

Un LLM aurait pu améliorer certains points :

- reformulation automatique des exigences ;
- rapprochement sémantique plus souple entre le texte réglementaire et la fiche produit ;
- meilleure gestion de formulations indirectes ;
- détection plus fine d'incohérences textuelles.

## 14. Limites d'un LLM dans ce contexte

Dans ce cas précis, un LLM aurait aussi eu plusieurs limites :

- résultats moins déterministes ;
- difficulté à garantir une justification stable d'une exécution à l'autre ;
- risque de conclure trop vite à une conformité ;
- risque d'halluciner une exigence ou une interprétation réglementaire ;
- difficulté à auditer précisément la logique de décision.

## 15. Limites actuelles de ma solution

Cette implémentation reste volontairement simple.

Ses principales limites sont :

- les règles sont en partie codées article par article ;
- la solution est adaptée au corpus fourni, pas à n'importe quelle directive ;
- la normalisation sémantique reste légère ;
- certaines décisions de sévérité reposent encore sur une interprétation humaine raisonnable.

## 16. Améliorations possibles

Si le périmètre devait être étendu, j'améliorerais la solution avec :

- une normalisation de texte plus poussée ;
- un moteur de règles configurable par fichier ;
- une extraction plus générique des obligations ;
- un export du rapport en JSON ou Markdown ;
- une couche de similarité sémantique locale ;
- éventuellement un LLM local ou API en second niveau, uniquement pour assister l'analyse et non pour décider seul.

## 17. Conclusion

J'ai privilégié une solution :

- simple ;
- modulaire ;
- déterministe ;
- lisible ;
- testable ;
- honnête sur ses limites.
