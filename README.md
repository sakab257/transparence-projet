# 🥗 SuperNutriScore

## 📌 Utilisation de l'IA

Nous avons utilisé l'IA dans notre projet pour plusieurs objectifs :
- **Objectif 1** : Commenter notre code, car nous pensons que c'est une bonne pratique et permet au groupe (et au responsable) de comprendre facilement et rapidement ce que chaque bout de code fait.
- **Objectif 2** : Créer le README, car un README fait par l'IA est meilleur qu'un README fait par un étudiant (surtout avec le langage MarkDown) à notre avis.
- **Objectif 3** : Nous aider pour l'UI utilisateur, car nous n'étions pas totalement familiers avec Streamlit (la meilleure librairie pour montrer des données analysées)

## 📌 Description du projet

**SuperNutriScore** est un projet académique du Groupe BOUSKINE (M2 MIAGE SITN) à Dauphine-PSL qui implémente et compare trois méthodes d'évaluation nutritionnelle des boissons :

1. **Nutri-Score BOISSONS** (algorithme officiel mars 2025)
2. **ELECTRE TRI** (méthode de classification multicritère)
3. **SuperNutri-Score** (combinaison Nutri-Score + Green-Score + Label BIO)

---

## 🎯 Objectifs

- ✅ Implémenter l'algorithme Nutri-Score **spécifique aux boissons** (mars 2025)
- ✅ Développer une classification ELECTRE TRI avec profils limites optimisés
- ✅ Créer un SuperNutri-Score holistique intégrant l'impact environnemental
- ✅ Comparer les trois méthodes sur une base de 289 boissons
- ✅ Fournir une interface interactive pour l'exploration des données

---

## 📂 Structure du projet

```
supernutriscore_project/
│
├── supernutriscore.py          # Classes principales (NutriScore, ELECTRE TRI, SuperNutri-Score)
├── interface_streamlit.py      # Interface web interactive
├── analyser_donnees.py         # Script d'analyse et vérification
├── base_donnees_boissons.csv   # Base de données (289 produits)
└── README.md                   # Ce fichier
```

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Installation des dépendances

```bash
pip install pandas numpy streamlit plotly
```

---

## 💻 Utilisation

### 1️⃣ Interface Streamlit (recommandé)

Lancer l'interface web interactive :

```bash
streamlit run interface_streamlit.py
```

L'interface propose 5 pages :
- **🏠 Accueil** : Vue d'ensemble de la base de données
- **🧮 Calculateur Nutri-Score** : Calcul pour un produit (nouveau ou de la base)
- **📊 ELECTRE TRI** : Classification multicritère paramétrable
- **⭐ SuperNutri-Score** : Évaluation holistique combinée
- **📈 Analyse Comparative** : Comparaison des 3 méthodes

### 2️⃣ Script d'analyse

Pour une analyse en ligne de commande :

```bash
# Analyse complète de la base
python analyser_donnees.py

# Analyse d'un produit spécifique
python analyser_donnees.py "Coca-Cola"
```

### 3️⃣ Utilisation programmatique

```python
from supernutriscore import NutriScoreBoissons, ElectreTri, SuperNutriScore
import pandas as pd

# Charger les données
df = pd.read_csv('base_donnees_boissons.csv')

# Calculer le Nutri-Score d'une boisson
resultat = NutriScoreBoissons.calculer_score_nutritionnel(
    energie_kj=180,
    acides_gras_satures=0.0,
    sucres=10.6,
    sel=0.0,
    contient_edulcorants=False,
    proteines=0.0,
    fibres=0.0,
    fruits_legumes=0,
    est_eau=False
)

print(f"Score: {resultat['score']}, Label: {resultat['label']}")

# Classification ELECTRE TRI
from supernutriscore import creer_profils_limites, definir_poids_criteres

profils = creer_profils_limites(df)
poids = definir_poids_criteres()

electre = ElectreTri(poids, profils, lambda_seuil=0.6)
df_classifie = electre.classifier_base_donnees(df, 'pessimiste')

# SuperNutri-Score
super_score = SuperNutriScore.calculer_super_score(
    nutriscore='B',
    greenscore='C',
    label_bio='OUI',
    poids_nutri=0.5,
    poids_green=0.3,
    poids_bio=0.2
)

print(f"SuperNutri-Score: {super_score['classe']}")
```

---

## 🧮 Algorithme Nutri-Score BOISSONS

### Différences avec l'algorithme classique

L'algorithme pour les **boissons** diffère de celui des aliments solides :

1. **Échelle de points adaptée** : Seuils spécifiques pour 100ml
2. **Prise en compte des édulcorants** : +4 points à la composante négative
3. **Limite de points positifs** : Maximum 7 points (vs 15 pour les aliments)
4. **Classification différente** :
   - A : score ≤ -2 (eaux automatiquement A)
   - B : -1 à 2
   - C : 3 à 6
   - D : 7 à 9
   - E : ≥ 10

### Formule

```
Score = N - P

N (négatif, à limiter) = points_énergie + points_sucres + points_acides_gras_sat + points_sel + points_édulcorants
P (positif, à favoriser) = min(points_protéines + points_fibres + points_fruits_légumes, 7)
```

---

## 📊 Méthode ELECTRE TRI

### Principe

ELECTRE TRI est une méthode de **tri multicritère** qui affecte chaque boisson à une catégorie (A, B, C, D, E) en la comparant à des **profils de référence** (b1 à b6).

### Critères utilisés

| Critère | Type | Poids | Sens |
|---------|------|-------|------|
| Énergie (kJ) | Nutritionnel | 0.15 | Minimiser |
| Acides gras saturés (g) | Nutritionnel | 0.10 | Minimiser |
| Sucres (g) | Nutritionnel | 0.20 | Minimiser |
| Sel (g) | Nutritionnel | 0.10 | Minimiser |
| Protéines (g) | Nutritionnel | 0.10 | Maximiser |
| Fibres (g) | Nutritionnel | 0.10 | Maximiser |
| Fruits/Légumes (%) | Nutritionnel | 0.15 | Maximiser |
| Nombre d'additifs | Qualité | 0.10 | Minimiser |

### Profils limites

Les profils b1 à b6 sont créés automatiquement à partir des **quantiles** de la base de données :
- **b6** (meilleur) : classe A
- **b5** : frontière A/B
- **b4** : frontière B/C
- **b3** : frontière C/D
- **b2** : frontière D/E
- **b1** (pire) : classe E

### Procédures d'affectation

- **Pessimiste** : Compare de b6 à b1, classe dès qu'il y a surclassement
- **Optimiste** : Compare de b1 à b6, classe dès qu'il y a domination inverse

### Paramètres ajustables

- **λ (lambda)** : Seuil de concordance (0.6 par défaut)
- **Poids** : Importance de chaque critère (ajustable dans l'interface)

---

## ⭐ SuperNutri-Score

### Concept

Le **SuperNutri-Score** combine trois dimensions pour une évaluation holistique :

1. **Nutri-Score** (qualité nutritionnelle) - Poids par défaut : 50%
2. **Green-Score** (impact environnemental) - Poids par défaut : 30%
3. **Label BIO** (mode de production) - Poids par défaut : 20%

### Calcul

```python
# Normalisation des scores entre 0 (meilleur) et 1 (pire)
nutri_norm = label_to_score(nutriscore) / 4
green_norm = label_to_score(greenscore) / 6
bio_norm = 0 si BIO, 1 si NON-BIO

# Score pondéré
score_final = poids_nutri × nutri_norm + poids_green × green_norm + poids_bio × bio_norm

# Classification
A : score ≤ 0.2
B : 0.2 < score ≤ 0.4
C : 0.4 < score ≤ 0.6
D : 0.6 < score ≤ 0.8
E : score > 0.8
```

### Avantages

- ✅ Vision globale de la qualité (santé + environnement + éthique)
- ✅ Poids ajustables selon les priorités
- ✅ Favorise les produits sains ET durables

---

## 📈 Résultats attendus

### Concordance Nutri-Score vs ELECTRE TRI

D'après nos analyses :
- **Procédure pessimiste (λ=0.6)** : ~35-45% de concordance
- **Procédure optimiste (λ=0.6)** : ~40-50% de concordance
- **Procédure pessimiste (λ=0.7)** : ~30-40% de concordance

### Divergences observées

ELECTRE TRI tend à :
- Être plus sévère avec les produits riches en additifs
- Valoriser davantage les produits avec protéines/fibres
- Produire une distribution différente (moins de A, plus de C)

### SuperNutri-Score

- Environ **60-70% de concordance** avec le Nutri-Score seul
- Favorise les produits BIO et à faible impact environnemental
- Dégrade les scores des produits avec Green-Score défavorable

---

## 🎓 Utilisation pour la soutenance

### Éléments à présenter

1. **Algorithme Nutri-Score BOISSONS**
   - Différences avec l'algorithme classique
   - Vérification sur des exemples (Coca-Cola, eau, jus)

2. **ELECTRE TRI**
   - Justification des profils limites (quantiles)
   - Justification des poids (importance des sucres pour les boissons)
   - Comparaison pessimiste vs optimiste
   - Analyse de sensibilité sur λ

3. **SuperNutri-Score**
   - Pertinence de combiner 3 dimensions
   - Choix des poids par défaut
   - Top/Bottom produits

4. **Comparaison des 3 méthodes**
   - Matrices de confusion
   - Accuracy
   - Analyse par catégorie de produits

### Démonstration live

1. Lancer l'interface Streamlit
2. Calculer le Nutri-Score d'un Coca-Cola
3. Lancer ELECTRE TRI avec λ=0.6 pessimiste
4. Calculer le SuperNutri-Score
5. Comparer les 3 méthodes dans la page "Analyse Comparative"

---

## 📊 Base de données

### Source

Les données proviennent de **Open Food Facts** (https://world.openfoodfacts.org/)

### Statistiques

- **289 boissons** au total
- **6 catégories principales** : Eau, Soda, Jus de fruits, Thé, Café, Boissons lactées
- **Distribution Nutri-Score** :
  - A : ~30%
  - B : ~25%
  - C : ~15%
  - D : ~15%
  - E : ~15%
- **Produits BIO** : ~10%

### Colonnes importantes

| Colonne | Description |
|---------|-------------|
| `Nom_Produit` | Nom commercial |
| `Marque` | Marque du produit |
| `Categorie` | Catégorie (Eau, Soda, etc.) |
| `Energie_kJ` | Énergie en kJ/100ml |
| `Sucres_g` | Sucres en g/100ml |
| `Sel_g` | Sel en g/100ml |
| `Label_Nutriscore` | Label Nutri-Score de référence |
| `Label_Greenscore` | Label Green-Score |
| `Label_Bio` | OUI/NON |
| `Nombre_Additifs` | Nombre d'additifs |

---

## 🔧 Améliorations possibles

### Court terme
- [ ] Ajouter des seuils d'indifférence/préférence pour ELECTRE TRI
- [ ] Implémenter le veto pour les critères critiques
- [ ] Ajouter une analyse de sensibilité automatique

### Moyen terme
- [ ] Intégrer d'autres méthodes MCDA (PROMETHEE, TOPSIS)
- [ ] Analyse de clustering des produits
- [ ] Prédiction du Nutri-Score par Machine Learning

### Long terme
- [ ] Base de données plus large (tous les produits alimentaires)
- [ ] API REST pour interroger les calculs
- [ ] Système de recommandation personnalisé

---

## 📚 Références

1. **Nutri-Score**
   - Règlement d'usage officiel mars 2025 : https://www.santepubliquefrance.fr/nutri-score
   - Algorithme boissons : Annexe 2 du cahier des charges

2. **ELECTRE TRI**
   - Roy, B. (1991). "The outranking approach and the foundations of ELECTRE methods"
   - Mousseau, V., Slowinski, R., & Zielniewicz, P. (2000). "A user-oriented implementation of the ELECTRE-TRI method"

3. **Aide Multicritère à la Décision**
   - Figueira, J., Greco, S., & Ehrgott, M. (2005). "Multiple Criteria Decision Analysis"

---

## 👨‍💻 Auteurs

**Mehdi TAZEROUTI** - M2 MIAGE SITN, Université Paris Dauphine-PSL

**Salim BOUSKINE** - M2 MIAGE SITN, Université Paris Dauphine-PSL

Projet académique dans le cadre du cours "Transparence des algorithmes" - Groupe BOUSKINE

---

## 📝 Licence

Ce projet est réalisé à des fins pédagogiques dans le cadre d'un master universitaire.

---

## 🙏 Remerciements

- Open Food Facts pour les données
- Santé Publique France pour la méthodologie Nutri-Score
- L'équipe pédagogique de Dauphine-PSL

---

## ❓ FAQ

### Q: Pourquoi l'algorithme Nutri-Score est-il différent pour les boissons ?

**R:** Les boissons ont des caractéristiques nutritionnelles très différentes des aliments solides (faible densité énergétique, peu de protéines/fibres, présence d'édulcorants). L'algorithme a donc été adapté avec des seuils spécifiques pour 100ml.

### Q: Quelle procédure ELECTRE TRI choisir ?

**R:** 
- **Pessimiste** : Plus conservatrice, classe "par le bas". À utiliser si on veut être exigeant.
- **Optimiste** : Plus permissive, classe "par le haut". À utiliser pour valoriser les produits.

### Q: Comment interpréter le SuperNutri-Score ?

**R:** Un produit peut avoir un bon Nutri-Score mais un mauvais SuperNutri-Score s'il a un fort impact environnemental ou n'est pas BIO. C'est une vision plus holistique de la qualité.

### Q: Les poids ELECTRE TRI sont-ils arbitraires ?

**R:** Non, ils sont justifiés par l'importance relative de chaque critère pour les boissons. Les sucres ont un poids élevé (0.20) car c'est le critère le plus discriminant pour les boissons.

### Q: Pourquoi certains produits ont des scores différents entre Nutri-Score et ELECTRE TRI ?

**R:** ELECTRE TRI prend en compte **8 critères** (dont les additifs) tandis que le Nutri-Score n'en utilise que **7**. De plus, les méthodes de pondération sont différentes.

---

**🎯 Pour toute question, consulter l'interface Streamlit qui contient des explications détaillées sur chaque page !**
