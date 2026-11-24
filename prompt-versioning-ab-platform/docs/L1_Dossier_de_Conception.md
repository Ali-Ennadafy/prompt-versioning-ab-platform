# Compléments du Dossier de Conception — L1

**Référence :** CDC-IA-2026-P06  
**Projet :** Prompt Versioning and A/B Testing Platform  
**Version :** 1.0  
**Date :** 23 novembre 2026

---

# 2.4 Architecture API et interfaces utilisateur

## 2.4.1 Architecture de l'API REST

L'API REST constitue le point d'entrée principal des fonctionnalités métier de la plateforme. Elle est développée avec FastAPI et assure la communication entre l'interface utilisateur, les services métier et les composants de stockage et d'intelligence artificielle.

Les endpoints sont organisés par domaine fonctionnel afin de faciliter leur maintenance et leur évolution.

### Endpoints actuellement implémentés

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/` | Vérifier le fonctionnement de l'API |
| POST | `/templates/` | Créer un template et sa première version |
| GET | `/templates/` | Consulter la liste des templates |
| GET | `/templates/{template_id}` | Consulter un template et ses versions |
| POST | `/templates/{template_id}/versions/` | Créer une nouvelle version |
| GET | `/templates/{template_id}/versions/` | Consulter l'historique des versions |
| PATCH | `/templates/{template_id}/versions/{version_number}` | Refuser la modification d'une version immuable |
| GET | `/templates/{template_id}/diff` | Comparer deux versions |

Ces endpoints constituent le socle fonctionnel actuellement développé et testé.

### Endpoints prévus pour les phases suivantes

| Méthode | Endpoint proposé | Responsabilité |
|---|---|---|
| POST | `/experiments/` | Créer une campagne A/B |
| GET | `/experiments/` | Consulter les campagnes |
| GET | `/experiments/{experiment_id}` | Consulter une campagne |
| POST | `/experiments/{experiment_id}/start` | Démarrer une campagne |
| POST | `/generate` | Distribuer une requête vers une variante et interroger le LLM local |
| GET | `/experiments/{experiment_id}/results` | Consulter les résultats |
| POST | `/evaluations/` | Enregistrer une évaluation humaine à l'aveugle |
| GET | `/experiments/{experiment_id}/statistics` | Consulter l'analyse statistique |
| POST | `/production/promote` | Promouvoir une version validée |
| POST | `/production/rollback` | Restaurer une version précédente |
| GET | `/health` | Vérifier l'état de l'application |

Les routes prévues seront définies et implémentées progressivement. Leur présence dans ce dossier décrit l'architecture cible et ne signifie pas qu'elles sont déjà disponibles.

## 2.4.2 Architecture de l'interface utilisateur

L'interface utilisateur sera développée avec Streamlit. Elle communiquera avec l'API FastAPI afin de séparer la présentation des traitements métier.

La plateforme comportera trois espaces fonctionnels principaux :

**1. Studio de Versionnage**

- Afficher les templates de prompts.
- Consulter les versions successives.
- Créer une nouvelle version.
- Visualiser les différences entre deux versions avec Diff.
- Identifier les versions verrouillées et la version de production.

**2. Arène de Test à l'Aveugle**

- Présenter deux réponses générées à partir des variantes A et B.
- Masquer l'identité de la variante source.
- Randomiser l'ordre d'affichage.
- Enregistrer le choix ou le score de préférence de l'évaluateur sans stocker son identité personnelle en clair.

**3. Tableau de Bord d'Expérimentation**

- Afficher les campagnes A/B.
- Présenter la distribution du trafic entre A et B.
- Afficher les métriques techniques.
- Comparer les résultats des variantes.
- Présenter les résultats statistiques et leur niveau de significativité.
- Permettre la promotion ou le rollback d'une version.

Ces interfaces seront intégrées progressivement selon le calendrier du projet.

## 2.4.3 Flux général de traitement d'une requête A/B

Lorsqu'une requête est envoyée pendant une campagne A/B, le système suit le processus suivant :

1. L'utilisateur transmet une requête à l'API.
2. L'Experiment Manager vérifie l'état de la campagne et les variantes configurées.
3. Le Traffic Router sélectionne la variante A ou B selon le ratio d'exposition défini.
4. Le système récupère la version de prompt associée à la variante sélectionnée.
5. Les variables dynamiques sont validées et injectées dans le prompt.
6. Le prompt est envoyé au modèle LLM local via Ollama.
7. La réponse générée est retournée et les métriques techniques sont calculées.
8. Les informations relatives à l'exécution sont enregistrées dans SQLite.
9. Les évaluations humaines peuvent être associées aux résultats.
10. Le Statistical Engine analyse les données disponibles afin de comparer les variantes.
11. Après validation des résultats, le Production Manager peut promouvoir la variante retenue ou effectuer un rollback.

---

# 3. Conception de la base de données

## 3.2.1 Modèle relationnel détaillé

Le modèle relationnel cible repose sur plusieurs entités permettant de conserver l'historique des prompts et de tracer les expérimentations.

### A. PromptTemplate

Cette table représente un modèle de prompt métier.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| name | String | Nom du template |
| description | Text | Description du cas métier |
| created_at | DateTime | Date de création |

### B. PromptVersion

Cette table conserve les différentes versions d'un template.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| template_id | Integer | Référence au template |
| version_number | Integer | Numéro de version |
| prompt_text | Text | Contenu du prompt |
| variables | JSON/Text | Variables dynamiques |
| author | String | Auteur de la modification |
| commit_message | String | Motif de création de la version |
| is_locked | Boolean | Indique si la version est verrouillée |
| is_production | Boolean | Indique si la version est en production |
| created_at | DateTime | Date de création |

Une contrainte d'unicité sur `(template_id, version_number)` garantit qu'un même template ne possède pas deux versions portant le même numéro.

Une version ayant déjà reçu du trafic dans une expérience A/B doit être verrouillée en lecture seule afin de préserver l'intégrité des résultats historiques.

### C. Experiment

Cette table représente une campagne d'expérimentation A/B.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| name | String | Nom de la campagne |
| description | Text | Objectif de l'expérience |
| traffic_ratio | JSON/Text | Ratio de répartition configuré |
| status | String | État de la campagne |
| created_at | DateTime | Date de création |
| started_at | DateTime | Date de démarrage |
| ended_at | DateTime | Date de fin |

### D. ExperimentVariant

Cette table représente une variante utilisée dans une expérience.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| experiment_id | Integer | Référence à l'expérience |
| prompt_version_id | Integer | Référence à la version du prompt |
| variant_label | String | Identifiant de la variante, A ou B |

Chaque variante référence une version précise et immuable d'un prompt.

### E. ExperimentResult

Cette table conserve les résultats de chaque exécution.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| variant_id | Integer | Variante exécutée |
| input_data | JSON/Text | Données d'entrée |
| generated_response | Text | Réponse produite par le LLM |
| latency_ms | Float | Temps de génération |
| created_at | DateTime | Date de l'exécution |

### F. Metric

Cette table conserve les indicateurs calculés à partir des résultats.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| result_id | Integer | Résultat associé |
| response_length | Integer | Longueur de la réponse |
| format_valid | Boolean | Conformité au format attendu |
| success | Boolean | Indicateur de réussite, selon le critère défini |

### G. HumanEvaluation

Cette table conserve les évaluations humaines anonymisées.

| Attribut | Type indicatif | Description |
|---|---|---|
| id | Integer | Identifiant unique |
| result_id | Integer | Résultat évalué |
| anonymous_vote | String | Vote ou préférence enregistrée |
| score | Float | Score éventuel |
| created_at | DateTime | Date de l'évaluation |

Aucune identité personnelle de l'évaluateur ne doit être stockée en clair.

## 3.2.2 Relations entre les entités

Les relations principales du modèle sont les suivantes :

- Un `PromptTemplate` possède plusieurs `PromptVersion`.
- Une `PromptVersion` appartient à un seul `PromptTemplate`.
- Une `Experiment` possède plusieurs `ExperimentVariant`.
- Une `ExperimentVariant` référence une seule `PromptVersion`.
- Une `ExperimentVariant` peut produire plusieurs `ExperimentResult`.
- Un `ExperimentResult` possède ses métriques dans `Metric`.
- Un `ExperimentResult` peut recevoir une ou plusieurs évaluations dans `HumanEvaluation`.

### Contraintes d'intégrité

Le système doit respecter les règles suivantes :

- Les numéros de versions sont uniques pour chaque template.
- Une variante doit référencer une version existante.
- Une exécution doit être associée à une variante de l'expérience.
- Une version ayant reçu du trafic expérimental ne peut plus être modifiée.
- Les résultats historiques doivent être conservés.
- Les évaluations humaines doivent rester anonymisées.

## 3.2.3 État d'implémentation du modèle

Dans la première phase, seules les entités `PromptTemplate` et `PromptVersion` sont effectivement implémentées dans SQLite.

Les entités `Experiment`, `ExperimentVariant`, `ExperimentResult`, `Metric` et `HumanEvaluation` appartiennent au modèle relationnel cible. Elles seront ajoutées lors des phases de développement correspondantes.

Les types de données indiqués dans les tableaux constituent une proposition logique de conception. Les types physiques définitifs seront adaptés à l'implémentation SQLAlchemy.

---

# 3.3 Choix et justification des tests statistiques

## 3.3.1 Objectif de l'analyse statistique

L'objectif du module statistique est de comparer les performances des variantes A et B afin de déterminer si les différences observées sont statistiquement significatives.

La plateforme ne doit pas déclarer automatiquement une variante gagnante sur la seule base d'une différence observée dans les résultats.

L'analyse statistique permet de limiter les décisions prématurées et de distinguer les différences potentiellement réelles des variations dues au hasard.

## 3.3.2 Tests statistiques retenus

Conformément aux spécifications techniques du cahier des charges, trois tests statistiques sont retenus.

### A. Test du Chi-deux (Chi-square)

Le test du Chi-deux permet de comparer des proportions entre deux variantes.

Il sera utilisé notamment pour comparer :

- Les taux de conformité au format attendu.
- Les taux de réussite.
- Les proportions de réponses respectant une règle définie.

Exemple : comparer le pourcentage de réponses JSON valides générées par la variante A avec celui de la variante B.

### B. Test exact de Fisher

Le test exact de Fisher permet de comparer des proportions lorsque les effectifs sont faibles, notamment lorsque les conditions d'application du test du Chi-deux ne sont pas satisfaites.

Il sera utilisé pour les tableaux de contingence présentant de faibles effectifs.

Ce test permet d'éviter de tirer des conclusions peu fiables lorsque le nombre d'observations dans certaines catégories est limité.

### C. Test t de Student

Le test t de Student permet de comparer les moyennes d'une variable numérique entre deux groupes.

Il pourra être utilisé notamment pour comparer :

- Le temps moyen de génération.
- La longueur moyenne des réponses.
- D'autres mesures numériques collectées pendant les campagnes.

Les conditions d'application du test seront vérifiées avant son utilisation, notamment la nature des données et les hypothèses nécessaires à l'interprétation du résultat.

## 3.3.3 Critère de significativité

Le seuil de significativité retenu est :

**p-value < 0,05**

Une p-value inférieure à 0,05 indique que la différence observée est statistiquement significative au seuil de 5 %, sous réserve des hypothèses du test utilisé.

Si la p-value est supérieure ou égale à 0,05, la plateforme ne devra pas déclarer de gagnant statistiquement confirmé.

Le résultat devra être présenté comme non significatif ou insuffisant pour conclure.

La significativité statistique ne signifie pas nécessairement que la différence possède une importance métier. Les métriques et les objectifs de l'expérience doivent également être pris en compte.

## 3.3.4 Règles de décision

Le processus de décision suivra les étapes suivantes :

1. Collecter les résultats des variantes A et B.
2. Calculer les indicateurs descriptifs.
3. Identifier la nature de la métrique analysée.
4. Sélectionner le test statistique approprié.
5. Calculer la p-value.
6. Comparer la p-value au seuil de 0,05.
7. Présenter le résultat et son interprétation.
8. Autoriser une promotion uniquement après analyse des résultats et validation de la campagne.

Une campagne présentant un échantillon insuffisant ne devra pas conduire à une déclaration prématurée de victoire.

Le cahier des charges prévoit une vérification statistique sur au moins 30 essais pour l'objectif de significativité et une vérification de la fidélité du split trafic sur au moins 40 requêtes.

## 3.3.5 Outil d'implémentation

Le module statistique sera développé en Python à l'aide de la bibliothèque SciPy.

Les résultats des tests seront conservés et présentés dans le tableau de bord afin de faciliter l'interprétation des campagnes.

---

# 3.4 Répartition des responsabilités du binôme

Le projet étant réalisé par un binôme, la répartition des responsabilités vise à organiser le développement tout en assurant l'intégration des différents composants.

La répartition suivante constitue une proposition de travail à valider par les deux stagiaires et l'encadrant pédagogique.

| Responsable | Responsabilités principales |
|---|---|
| Ali Ennadafy — Stagiaire 1 | Développement backend FastAPI, conception SQLite, modèles SQLAlchemy, gestion des templates et des versions, variables dynamiques, Diff et API de routage A/B |
| Isaac Smith — Stagiaire 2 | Préparation des jeux de données, intégration du LLM local via Ollama, collecte des métriques, évaluation humaine, analyse statistique et interface Streamlit |
| Travail commun | Conception globale, validation des choix techniques, tests d'intégration, campagnes A/B, documentation, déploiement et soutenance |

Les deux stagiaires participent à la validation des fonctionnalités et à la résolution des problèmes d'intégration.

Cette répartition pourra être ajustée selon l'avancement du projet et les besoins techniques.

---

# 4. Sécurité, qualité et contraintes techniques

## 4.1 Immuabilité des versions

Les versions de prompts sont conservées dans un historique structuré.

Une nouvelle modification doit donner lieu à la création d'une nouvelle version au lieu de modifier directement une ancienne version.

Toute version ayant reçu du trafic dans une expérience A/B devient verrouillée en lecture seule.

Ce mécanisme garantit la reproductibilité des expériences et protège l'intégrité des résultats historiques.

## 4.2 Validation des variables dynamiques

Avant la sauvegarde d'une version, le système vérifie la syntaxe des variables dynamiques présentes dans le prompt.

Les variables utilisent la notation `{variable}`.

Lors de l'exécution, les données fournies doivent être validées avant leur injection dans le prompt.

Cette validation permet de limiter les erreurs de format et les injections de données incorrectes.

## 4.3 Anonymisation des évaluations humaines

Lors des évaluations à l'aveugle :

- L'identité des variantes A et B doit être masquée.
- L'ordre de présentation des réponses doit être aléatoire.
- Les informations personnelles des évaluateurs ne doivent pas être stockées en clair.
- Les données clients réelles doivent être exclues ou anonymisées.

Ces règles visent à réduire les biais d'évaluation et à respecter les exigences de confidentialité.

## 4.4 Contraintes de performance

La plateforme devra respecter les objectifs de performance suivants :

| Indicateur | Objectif |
|---|---|
| Fidélité du split trafic | Écart inférieur ou égal à ±5 % |
| Échantillon pour vérifier le split | Au moins 40 requêtes |
| Significativité statistique | p-value < 0,05 |
| Conformité du format de sortie | Mesurée en pourcentage |
| Surcharge de la plateforme | Inférieure à 25 ms, hors génération LLM |

La mesure de la surcharge de la plateforme doit exclure le temps de génération du modèle LLM.

## 4.5 Environnement de déploiement

La plateforme sera exécutée localement, sans dépendance obligatoire à des services Cloud payants.

Les technologies principales sont :

- Python et FastAPI pour le backend.
- SQLite pour la persistance des données.
- SQLAlchemy pour l'accès relationnel.
- Ollama pour l'exécution du LLM local.
- SciPy pour les tests statistiques.
- Streamlit pour le tableau de bord.
- Docker ou Docker Compose pour le packaging final.

---

# 5. Conclusion du dossier de conception

Ce dossier présente la conception générale de la plateforme de versionnage de prompts et d'expérimentation A/B.

L'architecture proposée repose sur une séparation des responsabilités entre la présentation, l'API REST, la logique métier, l'accès aux données, l'intelligence artificielle et l'analyse statistique.

Le premier socle fonctionnel, constitué du registre de prompts, du versionnage, de la gestion des variables dynamiques et du comparateur Diff, est développé avec Python, FastAPI, SQLAlchemy et SQLite.

Les composants d'expérimentation A/B, de routage du trafic, de génération via Ollama, de collecte des métriques, d'évaluation humaine et d'analyse statistique seront intégrés progressivement selon le calendrier du projet.

La conception tient compte des exigences de traçabilité, d'immuabilité, d'anonymisation et de reproductibilité des expérimentations.

L'objectif final est de fournir une plateforme locale permettant de comparer objectivement différentes versions de prompts, d'identifier les variantes les plus performantes et de gérer leur promotion en production.

---

# 6. Références au cahier des charges

La conception présentée dans ce document s'appuie sur les exigences du cahier des charges CDC-IA-2026-P06, notamment :

- OBJ-01 : Référentiel de prompts versionnés.
- OBJ-02 : Répartition expérimentale du trafic A/B.
- OBJ-03 : Collecte des métriques et évaluation à l'aveugle.
- OBJ-04 : Analyse statistique et désignation du gagnant.
- OBJ-05 : Promotion en production et packaging.
- EF-01 à EF-06 : Exigences fonctionnelles.
- L1 : Dossier de Conception et Protocole A/B.
- REC-01 à REC-04 : Critères de recette.

**Fin du document — Dossier de Conception L1**