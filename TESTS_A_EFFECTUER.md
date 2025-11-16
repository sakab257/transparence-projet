# Tests à effectuer - SuperNutriScore V2

Ce document liste tous les tests à effectuer pour vérifier que le projet est conforme aux exigences.

## 1. Vérifications de la base de données

### Test 1.1 : Nombre total de produits
```bash
python3 -c "import pandas as pd; df = pd.read_csv('base_donnees_boissons.csv'); print(f'Nombre de produits: {len(df)}')"
```
**Résultat attendu** : ≥ 100 produits

### Test 1.2 : Pourcentage de produits BIO
```bash
python3 -c "import pandas as pd; df = pd.read_csv('base_donnees_boissons.csv'); bio = (df['Label_Bio'] == 'OUI').sum(); print(f'Produits BIO: {bio}/{len(df)} = {bio/len(df)*100:.1f}%')"
```
**Résultat attendu** : ≥ 25% de produits BIO

### Test 1.3 : Distribution Nutri-Score
```bash
python3 -c "import pandas as pd; df = pd.read_csv('base_donnees_boissons.csv'); print('Distribution Nutri-Score:'); print(df['Label_Nutriscore'].value_counts().sort_index()); print(f'\nMinimum par classe: {df[\"Label_Nutriscore\"].value_counts().min()}')"
```
**Résultat attendu** : Toutes les classes (A, B, C, D, E) ont ≥ 20 produits

### Test 1.4 : Distribution Green-Score
```bash
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('base_donnees_boissons.csv')
df_green = df[~df['Label_Greenscore'].isin(['NOT-APPLICABLE', 'UNKNOWN', 'F'])]
print('Distribution Green-Score (classes valides):')
print(df_green['Label_Greenscore'].value_counts().sort_index())
print(f'\nMinimum par classe: {df_green["Label_Greenscore"].value_counts().min()}')
EOF
```
**Résultat attendu** : Toutes les classes (A, A-PLUS, B, C, D, E) ont ≥ 10 produits

### Test 1.5 : Vérifier qu'il n'y a pas de valeurs aberrantes
```bash
python3 -c "import pandas as pd; df = pd.read_csv('base_donnees_boissons.csv'); aberrants = df[(df['Fibres_g'] > 5) | (df['Energie_kJ'] > 400)]; print(f'Produits aberrants (concentrés/poudres): {len(aberrants)}')"
```
**Résultat attendu** : 0 produit aberrant

---

## 2. Tests des algorithmes

### Test 2.1 : Analyse complète
```bash
python3 analyser_donnees.py
```
**À vérifier** :
- [x] Chargement de 284 produits
- [x] Algorithme Nutri-Score BOISSONS (mars 2025)
- [x] L'eau obtient automatiquement le label A
- [x] Concordance [OK] sur les produits testés
- [x] ELECTRE TRI génère les 6 profils (b1 à b6)
- [x] Les 2 procédures (pessimiste/optimiste) fonctionnent
- [x] SuperNutri-Score calcule les scores
- [x] Affichage des top 5 meilleurs/pires produits
- [x] Aucune erreur affichée

### Test 2.2 : Analyse d'un produit spécifique (Coca-Cola)
```bash
python3 analyser_donnees.py "Coca"
```
**À vérifier** :
- [x] Affiche les informations du produit
- [x] Calcule le Nutri-Score BOISSONS
- [x] Affiche les détails (composante N et P)
- [x] Calcule le SuperNutri-Score

### Test 2.3 : Analyse d'un produit spécifique (Eau)
```bash
python3 analyser_donnees.py "Evian"
```
**À vérifier** :
- [x] L'eau obtient automatiquement le label A
- [x] Score calculé = -10 (score eau par défaut)

### Test 2.4 : Vérifier les poids ELECTRE TRI
```bash
python3 -c "from supernutriscore import definir_poids_criteres; poids = definir_poids_criteres(); print('Poids des critères:'); [print(f'  {k}: {v:.2f}') for k, v in poids.items()]; print(f'\nSomme des poids: {sum(poids.values()):.2f}')"
```
**Résultat attendu** : Somme des poids = 1.00

---

## 3. Tests de l'interface Streamlit

### Test 3.1 : Lancer l'interface
```bash
streamlit run interface_streamlit.py
```

### Test 3.2 : Page Accueil
**À vérifier** :
- [ ] Titre du projet affiché
- [ ] Statistiques de la base de données
- [ ] Distribution des labels Nutri-Score
- [ ] Nombre de produits BIO
- [ ] Aucun emoji dans le texte

### Test 3.3 : Page Calculateur Nutri-Score
**À tester** :
1. Entrer les valeurs d'un produit (ex: Coca-Cola)
   - Énergie: 180 kJ
   - Sucres: 10.6g
   - Sel: 0g
   - Acides gras saturés: 0g
   - Protéines: 0g
   - Fibres: 0g
   - Fruits/Légumes: 0%
   - Édulcorants: Non
   - Type: Soda

**À vérifier** :
- [ ] Le score est calculé automatiquement
- [ ] Le label est affiché (attendu: E)
- [ ] Les détails (N et P) sont affichés
- [ ] Pas d'erreur

### Test 3.4 : Page ELECTRE TRI
**À tester** :
1. Sélectionner "Pessimiste" et λ=0.6
2. Sélectionner "Optimiste" et λ=0.6
3. Sélectionner "Pessimiste" et λ=0.7
4. Sélectionner "Optimiste" et λ=0.7

**À vérifier pour chaque test** :
- [ ] Matrice de confusion affichée avec :
  - Axe X (horizontal) : A', B', C', D', E' (nouveau score ELECTRE)
  - Axe Y (vertical) : A, B, C, D, E (Nutri-Score référence)
- [ ] Accuracy affichée
- [ ] Distribution des classes affichée
- [ ] Graphiques clairs et lisibles

### Test 3.5 : Page SuperNutri-Score
**À vérifier** :
- [ ] Matrice de confusion SuperNutri vs Nutri-Score
- [ ] Top 5 meilleurs produits (attendu: produits BIO classe A)
- [ ] Top 5 pires produits (attendu: produits classe E)
- [ ] Distribution des classes SuperNutri-Score
- [ ] Graphiques affichés correctement

### Test 3.6 : Page Analyse Comparative
**À vérifier** :
- [ ] Tableau comparatif des 5 méthodes :
  - ELECTRE TRI Pessimiste λ=0.6
  - ELECTRE TRI Optimiste λ=0.6
  - ELECTRE TRI Pessimiste λ=0.7
  - ELECTRE TRI Optimiste λ=0.7
  - SuperNutri-Score
- [ ] Graphique de comparaison des accuracy
- [ ] Analyse par catégorie (top 5 catégories)
- [ ] Pour chaque catégorie : distribution Nutri-Score, moyenne Sucres, moyenne Additifs

---

## 4. Vérifications du code

### Test 4.1 : Vérifier qu'il n'y a pas d'emojis
```bash
grep -r "[\U0001F600-\U0001F64F]" *.py || echo "Aucun emoji trouvé ✓"
```
**Résultat attendu** : Aucun emoji trouvé

### Test 4.2 : Vérifier que tous les fichiers sont présents
```bash
ls -lh base_donnees_boissons.csv supernutriscore.py analyser_donnees.py interface_streamlit.py
```
**Résultat attendu** : Les 4 fichiers sont présents

### Test 4.3 : Vérifier les imports
```bash
python3 -c "import supernutriscore; print('supernutriscore.py: OK')"
```
**Résultat attendu** : Pas d'erreur d'import

---

## 5. Tests de validation finale

### Test 5.1 : Exécuter tous les tests automatiquement
```bash
python3 << 'EOF'
import pandas as pd
from supernutriscore import definir_poids_criteres

print("=" * 80)
print("VALIDATION FINALE DU PROJET")
print("=" * 80)

# Test 1: Base de données
df = pd.read_csv('base_donnees_boissons.csv')
print(f"\n[TEST 1] Nombre de produits: {len(df)} (≥100 requis)")
assert len(df) >= 100, "ÉCHEC: Moins de 100 produits"

# Test 2: Produits BIO
bio = (df['Label_Bio'] == 'OUI').sum()
pct_bio = bio / len(df) * 100
print(f"[TEST 2] Produits BIO: {bio}/{len(df)} = {pct_bio:.1f}% (≥25% requis)")
assert pct_bio >= 25, "ÉCHEC: Moins de 25% de produits BIO"

# Test 3: Distribution Nutri-Score
nutri_counts = df['Label_Nutriscore'].value_counts()
min_nutri = nutri_counts.min()
print(f"[TEST 3] Distribution Nutri-Score - minimum par classe: {min_nutri} (≥20 requis)")
assert min_nutri >= 20, "ÉCHEC: Une classe Nutri-Score a moins de 20 produits"

# Test 4: Poids ELECTRE TRI
poids = definir_poids_criteres()
somme_poids = sum(poids.values())
print(f"[TEST 4] Somme des poids ELECTRE TRI: {somme_poids:.2f} (1.00 requis)")
assert abs(somme_poids - 1.0) < 0.01, "ÉCHEC: Somme des poids != 1.0"

# Test 5: Valeurs aberrantes
aberrants = df[(df['Fibres_g'] > 5) | (df['Energie_kJ'] > 400)]
print(f"[TEST 5] Produits aberrants (concentrés): {len(aberrants)} (0 requis)")
assert len(aberrants) == 0, "ÉCHEC: Des produits concentrés/poudres sont présents"

print("\n" + "=" * 80)
print("TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS ✓")
print("=" * 80)
EOF
```

**Résultat attendu** : Tous les tests passent avec succès

---

## Checklist finale avant rendu

- [ ] Tous les tests de la base de données passent
- [ ] Tous les algorithmes fonctionnent correctement
- [ ] L'interface Streamlit est fonctionnelle sur toutes les pages
- [ ] Aucun emoji dans le code
- [ ] Les matrices de confusion ont les bons axes (X: A', B', C', D', E' / Y: A, B, C, D, E)
- [ ] Le code est propre et commenté
- [ ] Les 4 fichiers principaux sont présents
- [ ] La documentation est claire

---

## En cas d'erreur

Si un test échoue :

1. **Erreur "command not found: python"** → Utiliser `python3` au lieu de `python`
2. **Erreur "module not found"** → Installer les dépendances : `pip install pandas numpy streamlit plotly`
3. **Erreur de lecture CSV** → Vérifier que le fichier `base_donnees_boissons.csv` est bien encodé en UTF-8
4. **Interface Streamlit ne se lance pas** → Vérifier l'installation : `pip install streamlit`

---

## Commande rapide pour tout tester

```bash
# Test rapide complet
python3 analyser_donnees.py && echo "Analyse OK ✓" && streamlit run interface_streamlit.py
```

Ce fichier doit être mis à jour si de nouveaux tests sont nécessaires.
