# Analyse de corrélation Jeux Olympiques & Performance Socio‑Économique
<img width="1536" height="1024" alt="ChatGPT Image 6 déc  2025, 21_29_09" src="https://github.com/user-attachments/assets/c141e131-6eba-487c-a6c5-e345de724944" />


## Introduction

Ce projet vise à analyser les Jeux Olympiques et à explorer les liens potentiels entre les performances sportives des pays et leurs indicateurs socio‑économiques. Il combine trois environnements : Python, Tableau, et MySQL.

Objectifs :

-   Nettoyer, fusionner et structurer les données.
    
-   Construire un modèle décisionnel (tables de faits et dimensions).
    
-   Produire des indicateurs et KPI.
    
-   Explorer les corrélations avec des données socio‑économiques (Banque Mondiale).
    
-   Concevoir un dashboard interactif.
- ---
## Sources de données

### Fichiers initiaux

-   `athlete_events.csv`  : données des athlètes
    
-   `noc_regions.csv` : correspondance entre les codes NOC et les pays.
    

### Données socio‑économiques

Récupérées via l’API World Bank 

-----


## Exploration des données

   L’exploration initiale des différentes sources a été réalisée à l’aide de **pandas** afin d’évaluer la structure, la complétude et la qualité des variables disponibles.  
Les trois jeux de données présentent les caractéristiques suivantes :
#### **1. Données sportives — `athlete_events.csv`**

Le fichier contient  271 116 enregistrements décrivant les participations individuelles aux Jeux Olympiques.  
Il comporte 15 colonnes, majoritairement de type texte, et plusieurs variables numériques présentant des valeurs manquantes.

Principales observations :

-   Les colonnes Age, Height et Weight présentent un taux de valeurs manquantes significatif.
    
-   Les variables clés (ID, Name, Sex, Team, NOC, Sport, Event) sont complètes.
    
-   La colonne Medal est fortement lacunaire, ce qui est logique puisque seule une minorité d’athlètes obtient une médaille.
    
-   Le fichier occupe environ 31 Mo en mémoire.
    


#### **2. Données pays — `noc_regions.csv`**

Ce fichier de référence contient 230 codes NOC :

-   La colonne region présente 3 valeurs manquantes, nécessitant un enrichissement — notamment via la base World Bank.
    
-   La colonne notes est très peu peuplée (21 valeurs renseignées).
    
-   Structure compacte (≈5,5 Ko), exclusivement textuelle.
    



#### **3. Données socio-économiques — API World Bank (indicateurs consolidés)**

L’ensemble extrait contient 16 758 lignes correspondant au croisement pays–année et 10 indicateurs.

Points notables :

-   Les clés Year et Country Name sont complètes.
    
-   Certains indicateurs présentent des taux de complétude variables :
    
    -   Très bonne disponibilité : Population 15-64 ans (%), Population femmes (%), Population totale
        
    -   Plus lacunaires : Croissance PIB (%), GDP (USD)
        
    -   Très incomplète : Taux d’activité des femmes (%)
        
-   Le fichier contient aussi un identifiant harmonisé ISO3Code, facilitant les jointures avec d’autres sources.
---

 ## Nettoyage et transformation des données

L’objectif de cette étape est de préparer les trois jeux de données (`athlete_events.csv`, `noc_regions.csv`, `worldbank_indic.csv`) pour consolidation et analyse.  
Le nettoyage a été réalisé avec Python (pandas).

| Fichier | Colonne | Action réalisée | Méthode / Justification |
| ------------------ | ---------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **World Bank** | Noms de colonnes | Renommage pour harmonisation (`ISO3Code → NOC`, `Country Name → region`, etc.) | Facilite les jointures et simplifie l’écriture des scripts |
| **World Bank** | NOC | Suppression des lignes nulles | Les clés pays manquantes empêchent le merge avec d’autres tables |
| **World Bank** | PIB | Imputation des valeurs manquantes par moyenne par NOC | Permet d’avoir des valeurs cohérentes par pays sur toutes les années |
| **World Bank** | `per_pop_urbaine` | Imputation par médiane par NOC | Réduit l’impact des valeurs extrêmes et conserve la distribution locale |
| **World Bank** | `Population Totale` | Imputation par médiane par NOC | Garantit des données complètes pour calculs de ratios |
| **World Bank** | `per_Taux_ActivFemmes` | Imputation par valeur minimale par NOC | Assure qu’aucune valeur n’est perdue pour cet indicateur souvent incomplet |
| **noc_regions** | region | Remplissage des valeurs manquantes via merge avec World Bank | Harmonisation des régions pour tous les NOC |
| **noc_regions** | notes | Suppression de la colonne | Peu informative et fortement lacunaire |
| **noc_regions** | NOC | Suppression des lignes `UNK` et `ROT` | Élimination des codes non pertinents pour l’analyse |
| **noc_regions** | doublons | Suppression des doublons (`NOC`, `region`) | Garantit l’unicité des lignes par NOC |
| **athlete_events** | Medal | Remplissage des valeurs manquantes par `"Aucune"` | Uniformisation de la variable pour analyses quantitatives et catégorielles |
| **athlete_events** | Age | Imputation par médiane regroupée par `Sport`, `Event`, `Year`, puis par `Sport` | Maintient la cohérence statistique des âges par discipline |
| **athlete_events** | Age | Conversion en entier | Normalisation des données pour les KPI et visualisations |
| **athlete_events** | Height, Weight, Games | Suppression des colonnes | Peu utilisées et fortement lacunaires |
| **athlete_events** | doublons | Suppression des doublons selon toutes les colonnes pertinentes | Évite les répétitions et garantit l’intégrité des données |
| **athlete_events** | NOC | Suppression des lignes `UNK` et `ROT` | Élimination des codes non pertinents |


**✅ Résultat :**

-   `athlEvent_clean.csv` : données athlètes nettoyées et harmonisées
    
-   `nocReg_clean.csv` : table de référence NOC/region complète
    
-   `world_clean.csv` : données socio-économiques nettoyées et imputées

----

## Fusion des données Athlètes et Référentiel NOC

L’objectif de cette étape est de consolider les informations des athlètes avec les données régionales des NOC pour disposer d’une table complète et exploitable pour l’analyse.
| Étape | Action réalisée | Méthode / Justification |
| -------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Importation** | Chargement des fichiers nettoyés `athlEvent_clean.csv` et `nocReg_clean.csv` | Utilisation de `pandas.read_csv` pour créer des DataFrames manipulables |
| **Fusion (merge)** | Merge des données athlètes avec les régions des NOC (`on='NOC', how='left'`) | Assure que chaque athlète est associé à la région correcte ; `left join` garantit que tous les athlètes sont conservés même si certaines régions sont manquantes |
| **Correction manuelle** | Pour le NOC `SGP`, attribution manuelle de la région `'Singapore'` | Correction spécifique pour gérer les valeurs manquantes non imputées automatiquement |
| **Vérification des doublons et nulls** | Inspection des valeurs `region` nulles par NOC | Permet de s’assurer que la fusion a bien complété la majorité des régions et identifier les rares cas nécessitant correction manuelle |
| **Export final** | Sauvegarde du fichier fusionné `merge_athl_reg_clean.csv` | Table consolidée prête pour la création des indicateurs dérivés et l’analyse |

**✅ Résultat :**

-   `merge_athl_reg_clean.csv` : table unique contenant toutes les informations athlètes enrichies avec leur région correspondante.
    
-   Prêt pour le calcul des KPI et l’analyse socio‑économique des performances olympiques.

## Fusion avec les données socio‑économiques (World Bank)

L’objectif de cette étape est de combiner les informations sur les participants olympiques par pays et par année avec les indicateurs socio‑économiques, afin de créer une table complète pour l’analyse des corrélations entre performances sportives et contexte socio‑économique.
| Étape | Action réalisée | Méthode / Justification |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Importation** | Chargement des fichiers `merge_athl_reg_clean.csv` et `world_clean.csv` | Utilisation de `pandas.read_csv` pour créer des DataFrames manipulables |
| **Comptage des participants par genre** | Création de deux DataFrames distincts : `df_femmes` et `df_hommes` regroupés par `NOC`, `Year`, `region` | Permet de connaître le nombre de participantes et participants par pays et par édition des Jeux Olympiques |
| **Renommage des colonnes** | `ID` → `nbr_partic_femmes` ou `nbr_partic_hommes` | Facilite la compréhension et le traitement des données |
| **Fusion hommes/femmes** | Merge des deux DataFrames pour obtenir une table unique par pays et par année (`how='outer'`) | Garantit que tous les pays et années avec des participants sont inclus, même si un genre est absent |
| **Conversion en entier** | Transformation des colonnes `nbr_partic_femmes` et `nbr_partic_hommes` en type `int` | Assure la cohérence des données pour les calculs et KPI |
| **Filtrage des données socio‑économiques** | Conservation uniquement des pays et années présents dans `df_athl_filt` | Réduit les données inutiles et évite les fusions avec des valeurs manquantes |
| **Fusion finale** | Merge `df_athl_filt` avec `df_wb_filtered` sur `NOC` et `Year` (`how='left'`) | Permet d’associer les indicateurs socio‑économiques (PIB, population, taux d’activité, etc.) aux données de participation olympique |
| **Nettoyage post-fusion** | Suppression de la colonne redondante `region_y`, renommage de `region_x` en `region` | Assure un DataFrame final clair et cohérent |
| **Export** | Sauvegarde en CSV : `merged_athwld.csv` | Table consolidée prête pour l’analyse des KPI et la visualisation |

-----
## Création des Tables de Dimensions

Après la consolidation des données, nous avons créé  les tables de dimensions nécessaires à la modélisation du modèle de données en étoile. Ces tables permettent de séparer les informations descriptives des données transactionnelles, facilitant les analyses et le calcul des KPI.

#### Table `dim_athlete`
| Colonne | Description |
| ------------ | ------------------------------- |
| `id_athlete` | Identifiant unique de l’athlète |
| `Name` | Nom complet de l’athlète |
| `Sex` | Sexe de l’athlète (M/F) |

**Méthode :**

-   Extraction des colonnes `ID`, `Name`, `Sex` depuis le DataFrame des athlètes
    
-   Suppression des doublons pour obtenir un identifiant unique par athlète
    
-   Sauvegarde au format CSV : `dim_athlete.csv`
    

**Objectif :**  
Permet d’analyser le profil des athlètes et de lier chaque performance sportive à un individu unique.

#### Table `dim_medal`
| Colonne | Description |
| --------------- | ------------------------------------------------------------------------------- |
| `id_medal` | Identifiant unique de la médaille |
| `type_medal` | Type de médaille : Gold, Silver, Bronze, Aucune |
| `score_pondere` | Score pondéré attribué à chaque médaille (Gold=3, Silver=2, Bronze=1, Aucune=0) |

**Méthode :**

-   Création d’une table listant tous les types de médailles
    
-   Attribution d’un score pondéré pour faciliter les analyses quantitatives
    
-   Sauvegarde en CSV : `dim_medal.csv`
    

**Objectif :**  
Standardiser les valeurs des médailles et permettre le calcul d’indicateurs de performance pondérés par type de médaille.

#### Table `dim_country`
| Colonne | Description |
| ------------ | ----------------------------------------------- |
| `id_country` | Identifiant unique du pays |
| `NOC` | Code officiel du Comité National Olympique |
| `region` | Région géographique ou continent associé au NOC |

**Méthode :**

-   Extraction des colonnes `NOC` et `region` depuis le DataFrame fusionné avec les indicateurs socio‑économiques
    
-   Suppression des doublons
    
-   Création d’un identifiant unique `id_country`
    
-   Sauvegarde en CSV : `dim_country.csv`
    

**Objectif :**  
Permet d’analyser les performances par pays et de relier les données socio‑économiques aux résultats sportifs.

#### Table `dim_event`
| Colonne | Description |
| ---------- | ---------------------------------- |
| `id_event` | Identifiant unique de l’événement |
| `Event` | Nom de l’événement sportif |
| `Season` | Saison (Summer / Winter) |
| `Sport` | Discipline sportive correspondante |

**Méthode :**

-   Extraction des colonnes `Event`, `Season`, `Sport` depuis le DataFrame des athlètes
    
-   Suppression des doublons
    
-   Création de l’identifiant unique `id_event`
    
-   Sauvegarde en CSV : `dim_event.csv`
    

**Objectif :**  
Faciliter l’analyse par discipline, événement et saison tout en normalisant les données.

#### Table `dim_date`
| Colonne | Description |
| --------- | ------------------------------ |
| `id_date` | Identifiant unique de l’année |
| `Year` | Année de l’événement olympique |

**Méthode :**

-   Extraction des années uniques depuis le DataFrame des athlètes
    
-   Création d’un identifiant unique `id_date`
    
-   Sauvegarde en CSV : `dim_date.csv`
    

**Objectif :**  
Permet d’analyser les performances et le nombre de participants par année, facilitant la création d’indicateurs temporels.

**✅ Résultat :**  
Ces tables de dimensions constituent la base du **modèle décisionnel** et seront utilisées pour créer la **table de faits principale**, en permettant une analyse rapide, cohérente et modulaire des performances olympiques.

----

## Création de la Table de Faits `fact_athlete`
----------
La table de faits `fact_athlete` centralise les informations quantitatives liées aux performances des athlètes et relie les tables de dimensions créées précédemment. Elle constitue la base du modèle décisionnel en étoile, permettant le calcul des KPI et l’analyse multi-dimensionnelle.



### Étapes de Construction

1.  **Chargement des données**
    
    -   Table des athlètes : `merge_athl_reg_clean.csv`
        
    -   Tables de dimensions : `dim_athlete`, `dim_country`, `dim_event`, `dim_date`, `dim_medal`


        
2.  **Normalisation et transformation des variables**
    
    -   Capitalisation de la colonne `Medal` pour uniformiser les valeurs.
        
    -   Création de l’indicateur `is_medalist` : 1 si l’athlète a remporté une médaille, 0 sinon.
        
    -   Attribution du score pondéré `score_pondere` selon le type de médaille : Gold = 3, Silver = 2, Bronze = 1, Aucune = 0.
        
3.  **Jointures avec les tables de dimensions**
    
    -   **Athlète** : fusion avec `dim_athlete` pour récupérer `id_athlete`.
        
    -   **Pays** : fusion avec `dim_country` pour récupérer `id_country`.
        
    -   **Event** : fusion avec `dim_event` pour récupérer `id_event`.
        
    -   **Date** : fusion avec `dim_date` pour récupérer `id_date`.
        
    -   **Medal** : fusion avec `dim_medal` pour récupérer `id_medal`.
        
4.  **Sélection des colonnes finales**  

    La table de faits ne conserve que :
    
    -   Clés étrangères vers les tables de dimensions : `id_athlete`, `id_country`, `id_event`, `id_date`, `id_medal`
        
    -   Mesures : `is_medalist`, `score_pondere`
        
6.  **Sauvegarde de la table**
    
    -   Export en CSV : `fact_athlete.csv`
        
    -   Cette table est maintenant prête pour le calcul des KPI et l’alimentation des dashboards.
    
 ### Structure de la Table `fact_athlete`
 
| Colonne | Description |
| --------------- | -------------------------------------------------------- |
| `id_athlete` | Clé étrangère vers `dim_athlete` |
| `id_country` | Clé étrangère vers `dim_country` |
| `id_event` | Clé étrangère vers `dim_event` |
| `id_date` | Clé étrangère vers `dim_date` |
| `id_medal` | Clé étrangère vers `dim_medal` |
| `is_medalist` | 1 si l’athlète a remporté une médaille, 0 sinon |
| `score_pondere` | Score pondéré de la médaille pour analyses quantitatives |
--- 
## Création de la Table de Faits `fact_world`
----
La table de faits `fact_world` centralise les indicateurs socio-économiques par pays et par année, et sert de référence pour l’analyse des corrélations entre la performance olympique et le contexte socio-économique.



###  Étapes de Construction

1.  **Chargement des données**
    
    -   Dataset principal : `merged_athwld.csv` contenant les informations socio-économiques filtrées par pays et années présentes dans les données athlètes.
        
    -   Tables de dimensions : `dim_country` et `dim_date`.
        
2.  **Jointures avec les tables de dimensions**
    
    -   **Pays** : ajout de l’identifiant unique `id_country` depuis `dim_country`.
        
    -   **Date** : ajout de l’identifiant unique `id_date` depuis `dim_date`.
        
3.  **Sélection des colonnes finales** 

    La table de faits contient :
    
    -   Clés étrangères : `id_country`, `id_date`
        
    -   Mesures et indicateurs :
        
        -   Nombre de participants : `nbr_partic_femmes`, `nbr_partic_hommes`
            
        -   Indicateurs démographiques : `per_Pop15_64`, `per_pop_femmes`, `per_pop_urbaine`
            
        -   Indicateurs économiques : `per_Crois_PIB`, `PIB`, `Population Totale`
            
        -   Indicateur d’activité féminine : `per_Taux_ActivFemmes`
            
5.  **Sauvegarde de la table**
    
    -   Export en CSV : `fact_world.csv`
        
    -   La table est prête pour l’analyse multidimensionnelle et le calcul des KPI socio-économiques associés à la performance olympique.
       

### Structure de la Table `fact_world`

| Colonne | Description |
| ---------------------- | ------------------------------------------------ |
| `id_country` | Clé étrangère vers `dim_country` |
| `id_date` | Clé étrangère vers `dim_date` |
| `nbr_partic_femmes` | Nombre de participantes féminines aux Jeux |
| `nbr_partic_hommes` | Nombre de participants masculins aux Jeux |
| `per_Pop15_64` | Pourcentage de la population âgée de 15 à 64 ans |
| `per_Crois_PIB` | Croissance du PIB (%) |
| `per_Taux_ActivFemmes` | Taux d’activité des femmes (%) |
| `per_pop_femmes` | Pourcentage de femmes dans la population totale |
| `per_pop_urbaine` | Pourcentage de la population urbaine |
| `PIB` | Produit Intérieur Brut (en USD) |
| `Population Totale` | Population totale du pays |

----

## Création de la Base de Données et des Tables dans MySQL Workbench
----------
Après avoir préparé et nettoyé les fichiers CSV avec Python, les tables de dimensions et de faits ont été importées dans MySQL.

### Base de données

-   Nom de la base de données : `olympic_project`

<img width="412" height="116" alt="database" src="https://github.com/user-attachments/assets/4202e474-dda4-49b8-9a3b-515d10911534" />

    
-   Cette base centralise toutes les informations relatives aux athlètes, aux médailles, aux événements et aux indicateurs socio-économiques des pays.

### Tables de Dimensions

Les tables de dimensions permettent de normaliser les données et d’éviter les redondances. Chaque table possède une clé primaire unique  utilisée dans les tables de faits.

<img width="245" height="537" alt="tables_dim" src="https://github.com/user-attachments/assets/21acec02-512a-4fe5-947c-d1b2e6bd160b" />



### Tables de Faits

Les tables de faits centralisent les mesures et références aux dimensions

<img width="457" height="315" alt="tables_fact_ath" src="https://github.com/user-attachments/assets/7cefff73-e8d0-432b-9728-b09620d46f67" />

<img width="443" height="306" alt="table_fact_world" src="https://github.com/user-attachments/assets/cb3c368e-746b-4cd3-bab4-bfd3d8157112" />




### Import des données

-   Les fichiers CSV (`dim_*.csv` et `fact_*.csv`) ont été importés via MySQL Workbench pour peupler les tables.

### Schéma Relationnel (Data Model) dans MySQL Workbench

Après la création des tables de dimensions et des tables de faits, un schéma relationnel a été conçu pour représenter visuellement les relations entre les différentes tables de la base `olympic_project`.

<img width="797" height="786" alt="schema_en_etoile_sql" src="https://github.com/user-attachments/assets/ae1f496d-0c5e-4723-83cc-4ff57a358b02" />


Objectif du schéma relationnel

-   Clarifier les relations entre les dimensions et les faits.
    
-   Assurer l’intégrité référentielle via les clés primaires et étrangères.
    
-   Faciliter les requêtes analytiques.
-----
## Préparation du Dashboard dans Tableau
----------
### Importation des données

-   Tous les fichiers CSV nettoyés et transformés ont été importés dans Tableau :
    
    -   `dim_athlete.csv`
        
    -   `dim_country.csv`
        
    -   `dim_event.csv`
        
    -   `dim_date.csv`
        
    -   `dim_medal.csv`
        
    -   `fact_athlete.csv`
        
    -   `fact_world.csv`
        
    

----------

###  Structuration du schéma relationnel

-   Dans Tableau, le schéma en étoile a été recréé en reliant les tables de faits aux tables de dimensions via les clés primaires et étrangères.


    <img width="627" height="532" alt="schema_en_etoile_tableau" src="https://github.com/user-attachments/assets/ef24fd70-8216-4a83-b53e-23479a121064" />
    

-   Relations principales établies :
    
    -   `fact_athlete` → `dim_athlete`, `dim_country`, `dim_event`, `dim_date`, `dim_medal`
        
    -   `fact_world` → `dim_country`, `dim_date`
        
-   Ce lien entre faits et dimensions permet de créer des calculs et visualisations dynamiques en filtrant par année, pays, sport, type de médaille, etc.
    

### KPI utilisés dans le Dashboard Jeux Olympiques


| **Nom du KPI**              | **Description**                                                                       | **Formule Tableau**                               | **Objectif / Utilité**                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Total Medals**            | Nombre total de médailles remportées par les athlètes.                                | `SUM([Is Medalist])`                              | Suivre la performance globale d’un pays ou d’un athlète.                                |
| **Médailles score pondéré** | Score pondéré des médailles pour valoriser les médailles d’or, argent et bronze.      | `SUM([Score Pondere])`                            | Permet de comparer la performance des pays en tenant compte de la valeur des médailles. |
| **Ratio Med_Urb**           | Ratio entre le nombre de médailles et la population urbaine du pays.                  | `SUM([Is Medalist]) / AVG([Per Pop Urbaine]/100)` | Mesure l’efficacité des athlètes par rapport à la population urbaine.                   |
| **TauxPartip_Hab**          | Proportion d’athlètes participants par rapport à la population active (15-64 ans).    | `COUNTD([Id Athlete]) / AVG([per Pop15_64])`      | Évaluer la participation relative d’un pays en fonction de sa population active.        |
| **Med_CroissPIB**           | Ratio de médailles par rapport à la croissance du PIB.                                | `SUM([Is Medalist]) / AVG([per Crois PIB])`       | Analyser la corrélation entre performance sportive et croissance économique.            |
| **Ratio Med_POPActive**     | Médailles par rapport à la population active (15-64 ans).                             | `SUM([Is Medalist]) / AVG([per Pop15_64])`        | Identifier l’efficacité sportive par rapport à la population active.                    |
| **ParticFemmes_POP1564**    | Proportion de participantes féminines par rapport à la population active (15-64 ans). | `SUM([Nbr Partic Femmes]) / AVG([per Pop15_64])`  | Suivre la participation féminine aux Jeux Olympiques.                                   |
| **ParticHommes_POP1564**    | Proportion de participants masculins par rapport à la population active (15-64 ans).  | `SUM([Nbr Partic Hommes]) / AVG([per Pop15_64])`  | Suivre la participation masculine aux Jeux Olympiques.                                  |
| **ScorePon_POP**            | Score pondéré des médailles ajusté par rapport à la population totale.                | `SUM([Score Pondere]) / AVG([Population Totale])` | Comparer la performance des pays en tenant compte de leur population totale.            |



### Construction du dashboard final

<img width="1600" height="798" alt="vision_tableau" src="https://github.com/user-attachments/assets/07eb88e3-599c-450b-8b07-7e3382b3d279" />
