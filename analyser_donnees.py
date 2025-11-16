import pandas as pd
from supernutriscore import (
    NutriScoreBoissons, ElectreTri, SuperNutriScore, AnalyseResultats,
    creer_profils_limites, definir_poids_criteres
)


def analyser_base_donnees():
    print("=" * 80)
    print("SUPERNUTRISCORE - Analyse complète")
    print("=" * 80)
    print()
    
    # Chargement des données
    print("[INFO] Chargement de la base de données...")
    try:
        df = pd.read_csv('base_donnees_boissons.csv', encoding='utf-8')
        df.columns = df.columns.str.strip()
        print(f"[OK] {len(df)} produits chargés")
        print()
    except Exception as e:
        print(f"[ERREUR] Erreur lors du chargement : {e}")
        return
    
    # Statistiques descriptives
    print("[STATS] Statistiques descriptives")
    print("-" * 80)
    print(f"Nombre total de produits: {len(df)}")
    print(f"\nDistribution des labels Nutri-Score:")
    print(df['Label_Nutriscore'].value_counts().sort_index())
    print(f"\nNombre de catégories: {df['Categorie'].nunique()}")
    print(f"Produits BIO: {(df['Label_Bio'] == 'OUI').sum()} ({(df['Label_Bio'] == 'OUI').sum()/len(df)*100:.1f}%)")
    print()
    
    # Vérification de l'algorithme Nutri-Score BOISSONS
    print("[CALCUL] Vérification de l'algorithme Nutri-Score BOISSONS")
    print("-" * 80)
    
    # Test avec plusieurs produits
    produits_test = [
        ('Coca-Cola', 6),
        ('Eau Evian', 18),
        ("Jus d'orange", 5)
    ]
    
    for nom, idx in produits_test:
        produit = df.iloc[idx]
        print(f"\nProduit: {produit['Nom_Produit']}")
        print(f"Catégorie: {produit['Categorie']}")
        
        # Détection eau
        est_eau = produit['Categorie'].lower() == 'eau'
        
        # Détection édulcorants
        contient_edulcorants = False
        if pd.notna(produit['Liste_Additifs']):
            edulcorants_codes = ['e950', 'e951', 'e952', 'e954', 'e955']
            contient_edulcorants = any(code in str(produit['Liste_Additifs']).lower() 
                                      for code in edulcorants_codes)
        
        resultat = NutriScoreBoissons.calculer_score_nutritionnel(
            produit['Energie_kJ'],
            produit['Acides_Gras_Satures_g'],
            produit['Sucres_g'],
            produit['Sel_g'],
            contient_edulcorants,
            produit['Proteines_g'],
            produit['Fibres_g'],
            produit['Fruits_Legumes_Pct'],
            est_eau
        )
        
        print(f"Score calculé: {resultat['score']} | Label: {resultat['label']}")
        print(f"Score DB: {produit['Score_Nutriscore']} | Label DB: {produit['Label_Nutriscore']}")
        concordance = "[OK]" if resultat['label'] == produit['Label_Nutriscore'] else "[X]"
        print(f"Concordance: {concordance}")
    
    print()
    
    # Classification ELECTRE TRI
    print("[STATS] Classification ELECTRE TRI")
    print("-" * 80)
    
    profils = creer_profils_limites(df)
    print("\nProfils limites créés:")
    print(profils)
    print()
    
    poids = definir_poids_criteres()
    print("Poids des critères:")
    for crit, val in poids.items():
        print(f"  {crit}: {val:.2f}")
    print()
    
    # Test avec λ=0.6
    print("Classification avec λ=0.6:")
    print()
    
    for methode in ['pessimiste', 'optimiste']:
        print(f"Procédure {methode.upper()}:")
        electre = ElectreTri(poids, profils, lambda_seuil=0.6)
        df_resultat = electre.classifier_base_donnees(df, methode)
        
        colonne = f'Classe_ELECTRE_{methode.capitalize()}'
        print(df_resultat[colonne].value_counts().sort_index())
        
        # Matrice de confusion
        matrice = AnalyseResultats.matrice_confusion(
            df_resultat['Label_Nutriscore'],
            df_resultat[colonne]
        )
        metriques = AnalyseResultats.calculer_metriques(matrice)
        print(f"Accuracy: {metriques['accuracy']:.2%}")
        print()
    
    # SuperNutri-Score
    print("[SUPER] Calcul du SuperNutri-Score")
    print("-" * 80)
    
    resultats_super = []
    for idx, row in df.iterrows():
        super_score = SuperNutriScore.calculer_super_score(
            row['Label_Nutriscore'],
            row['Label_Greenscore'] if pd.notna(row['Label_Greenscore']) else 'NOT-APPLICABLE',
            row['Label_Bio'],
            poids_nutri=0.5,
            poids_green=0.3,
            poids_bio=0.2
        )
        resultats_super.append(super_score['classe'])
    
    df['SuperNutri_Classe'] = resultats_super
    
    print("Distribution SuperNutri-Score:")
    print(df['SuperNutri_Classe'].value_counts().sort_index())
    print()
    
    # Matrice de confusion SuperNutri vs Nutri
    matrice_super = AnalyseResultats.matrice_confusion(
        df['Label_Nutriscore'],
        df['SuperNutri_Classe']
    )
    metriques_super = AnalyseResultats.calculer_metriques(matrice_super)
    print(f"Concordance SuperNutri-Score vs Nutri-Score: {metriques_super['accuracy']:.2%}")
    print()
    
    # Top 10 meilleurs et pires produits
    print("[TOP] Top 5 meilleurs produits (SuperNutri-Score):")
    df_super_score = []
    for idx, row in df.iterrows():
        super_score = SuperNutriScore.calculer_super_score(
            row['Label_Nutriscore'],
            row['Label_Greenscore'] if pd.notna(row['Label_Greenscore']) else 'NOT-APPLICABLE',
            row['Label_Bio']
        )
        df_super_score.append(super_score['score'])
    
    df['SuperNutri_Score'] = df_super_score
    
    top5 = df.nsmallest(5, 'SuperNutri_Score')[['Nom_Produit', 'Marque', 'SuperNutri_Classe', 'SuperNutri_Score']]
    print(top5.to_string(index=False))
    print()
    
    print("[INFO] Top 5 pires produits (SuperNutri-Score):")
    bottom5 = df.nlargest(5, 'SuperNutri_Score')[['Nom_Produit', 'Marque', 'SuperNutri_Classe', 'SuperNutri_Score']]
    print(bottom5.to_string(index=False))
    print()
    
    # Comparaison des méthodes
    print("[STATS] Comparaison des méthodes")
    print("-" * 80)
    
    comparaisons = []
    
    for lambda_val in [0.6, 0.7]:
        for methode in ['pessimiste', 'optimiste']:
            electre = ElectreTri(poids, profils, lambda_val)
            df_temp = electre.classifier_base_donnees(df, methode)
            
            colonne = f'Classe_ELECTRE_{methode.capitalize()}'
            matrice = AnalyseResultats.matrice_confusion(
                df_temp['Label_Nutriscore'],
                df_temp[colonne]
            )
            metriques = AnalyseResultats.calculer_metriques(matrice)
            
            comparaisons.append({
                'Méthode': f'ELECTRE TRI {methode.capitalize()} (λ={lambda_val})',
                'Accuracy': f"{metriques['accuracy']:.2%}"
            })
    
    comparaisons.append({
        'Méthode': 'SuperNutri-Score',
        'Accuracy': f"{metriques_super['accuracy']:.2%}"
    })
    
    df_comparaison = pd.DataFrame(comparaisons)
    print(df_comparaison.to_string(index=False))
    print()
    
    # Analyse par catégorie
    print("[CATEGORIE] Analyse par catégorie")
    print("-" * 80)
    
    top_categories = df['Categorie'].value_counts().head(5)
    
    for categorie in top_categories.index:
        df_cat = df[df['Categorie'] == categorie]
        print(f"\nCatégorie: {categorie} ({len(df_cat)} produits)")
        print(f"Distribution Nutri-Score:")
        print(df_cat['Label_Nutriscore'].value_counts().sort_index())
        print(f"Moyenne Sucres: {df_cat['Sucres_g'].mean():.1f}g/100ml")
        print(f"Moyenne Additifs: {df_cat['Nombre_Additifs'].mean():.1f}")
    
    print()
    print("=" * 80)
    print("[OK] ANALYSE TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print()
    print("[INFO] Pour visualiser les résultats de manière interactive:")
    print("   streamlit run interface_streamlit.py")
    print()
    print("[STATS] Toutes les analyses, graphiques et comparaisons sont disponibles")
    print("   dans l'interface Streamlit avec des visualisations interactives.")
    print()


def analyser_produit_specifique(nom_produit: str):
    df = pd.read_csv('base_donnees_boissons.csv', encoding='utf-8')
    df.columns = df.columns.str.strip()
    
    produit = df[df['Nom_Produit'].str.contains(nom_produit, case=False, na=False)]
    
    if len(produit) == 0:
        print(f"[ERREUR] Produit '{nom_produit}' non trouvé")
        return
    
    produit = produit.iloc[0]
    
    print("=" * 80)
    print(f"ANALYSE DÉTAILLÉE : {produit['Nom_Produit']}")
    print("=" * 80)
    print()
    
    print("[INFO] Informations générales")
    print(f"Marque: {produit['Marque']}")
    print(f"Catégorie: {produit['Categorie']}")
    print(f"Label BIO: {produit['Label_Bio']}")
    print()
    
    print("[ANALYSE] Composition nutritionnelle (pour 100ml)")
    print(f"Énergie: {produit['Energie_kJ']} kJ ({produit['Energie_kcal']} kcal)")
    print(f"Sucres: {produit['Sucres_g']}g")
    print(f"Acides gras saturés: {produit['Acides_Gras_Satures_g']}g")
    print(f"Sel: {produit['Sel_g']}g")
    print(f"Protéines: {produit['Proteines_g']}g")
    print(f"Fibres: {produit['Fibres_g']}g")
    print(f"Fruits/Légumes: {produit['Fruits_Legumes_Pct']}%")
    print(f"Nombre d'additifs: {produit['Nombre_Additifs']}")
    print()
    
    # Nutri-Score
    est_eau = produit['Categorie'].lower() == 'eau'
    contient_edulcorants = False
    if pd.notna(produit['Liste_Additifs']):
        edulcorants_codes = ['e950', 'e951', 'e952', 'e954', 'e955']
        contient_edulcorants = any(code in str(produit['Liste_Additifs']).lower() 
                                  for code in edulcorants_codes)
    
    resultat_nutri = NutriScoreBoissons.calculer_score_nutritionnel(
        produit['Energie_kJ'],
        produit['Acides_Gras_Satures_g'],
        produit['Sucres_g'],
        produit['Sel_g'],
        contient_edulcorants,
        produit['Proteines_g'],
        produit['Fibres_g'],
        produit['Fruits_Legumes_Pct'],
        est_eau
    )
    
    print("[CALCUL] Nutri-Score (algorithme boissons mars 2025)")
    print(f"Score: {resultat_nutri['score']}")
    print(f"Label: {resultat_nutri['label']}")
    print(f"Composante négative (N): {resultat_nutri['details']['score_negatif']}")
    print(f"Composante positive (P): {resultat_nutri['details']['score_positif']}")
    print()
    
    # SuperNutri-Score
    super_score = SuperNutriScore.calculer_super_score(
        produit['Label_Nutriscore'],
        produit['Label_Greenscore'] if pd.notna(produit['Label_Greenscore']) else 'NOT-APPLICABLE',
        produit['Label_Bio']
    )
    
    print("[SUPER] SuperNutri-Score")
    print(f"Classe: {super_score['classe']}")
    print(f"Score: {super_score['score']:.2f}")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analyse d'un produit spécifique
        nom_produit = " ".join(sys.argv[1:])
        analyser_produit_specifique(nom_produit)
    else:
        # Analyse complète
        analyser_base_donnees()
