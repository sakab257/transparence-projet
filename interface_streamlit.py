"""
Interface Streamlit - SuperNutriScore
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from supernutriscore import (
    NutriScoreBoissons, ElectreTri, SuperNutriScore, AnalyseResultats,
    creer_profils_limites, definir_poids_criteres
)

st.set_page_config(
    page_title="Projet Transparence - Mehdi, Salim",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<p class="main-header">Projet Transparence des algorithmes - Groupe BOUSKINE</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Évaluation nutritionnelle multicritère des boissons</p>', unsafe_allow_html=True)

# Navigation
st.sidebar.title("Naviguer entre les pages...")
page = st.sidebar.selectbox(
    "Choisissez une page",
    ["Accueil", "Calculateur Nutri-Score", 
     "ELECTRE TRI", "SuperNutri-Score", 
     "Analyse Comparative"]
)

# Chargement données
@st.cache_data
def charger_donnees():
    try:
        df = pd.read_csv('base_donnees_boissons.csv', encoding='utf-8')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None

df = charger_donnees()

# PAGE ACCUEIL
if page == "Accueil":
    st.markdown("## Bienvenue !")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        ### Nutri-Score Boissons
        - Algorithme officiel mars 2025
        - Spécifique aux boissons
        - Calcul transparent
        """)
    
    with col2:
        st.success("""
        ### ELECTRE TRI
        - Classification multicritère
        - Procédures pessimiste/optimiste
        - Profils personnalisables
        """)
    
    with col3:
        st.warning("""
        ### SuperNutri-Score
        - Nutri-Score + Green-Score + BIO
        - Évaluation holistique
        - Pondération ajustable
        """)
    
    if df is not None:
        st.markdown("---")
        st.markdown("### Statistiques de la base de données")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Produits", len(df), delta=None)
        with col2:
            n_marques = df['Marque'].nunique()
            st.metric("Marques", n_marques)
        with col3:
            n_categories = df['Categorie'].nunique()
            st.metric("Catégories", n_categories)
        with col4:
            pct_bio = (df['Label_Bio'] == 'OUI').sum() / len(df) * 100
            st.metric("% BIO", f"{pct_bio:.1f}%")
        with col5:
            avg_additifs = df['Nombre_Additifs'].mean()
            st.metric("Additifs (moy.)", f"{avg_additifs:.1f}")
        
        # Distribution des labels
        st.markdown("### Distribution des labels Nutri-Score")
        
        labels_count = df['Label_Nutriscore'].value_counts().sort_index()
        
        fig = px.bar(
            x=labels_count.index,
            y=labels_count.values,
            labels={'x': 'Label Nutri-Score', 'y': 'Nombre de produits'},
            color=labels_count.index,
            color_discrete_map={
                'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02',
                'D': '#EE8100', 'E': '#E63E11'
            },
            text=labels_count.values
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution par catégorie
        st.markdown("### Top 10 catégories")
        top_categories = df['Categorie'].value_counts().head(10)
        
        fig_cat = px.bar(
            x=top_categories.values,
            y=top_categories.index,
            orientation='h',
            labels={'x': 'Nombre de produits', 'y': 'Catégorie'},
            color=top_categories.values,
            color_continuous_scale='Viridis'
        )
        fig_cat.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)
        
        # Aperçu des données
        st.markdown("### Aperçu de la base de données")
        colonnes_affichage = ['Nom_Produit', 'Marque', 'Categorie', 'Label_Nutriscore', 
                             'Score_Nutriscore', 'Label_Bio', 'Nombre_Additifs']
        st.dataframe(df[colonnes_affichage].head(50), use_container_width=True)

# PAGE CALCULATEUR
elif page == "Calculateur Nutri-Score":
    st.markdown("## Calculateur Nutri-Score pour Boissons")
    st.info("**Algorithme officiel mars 2025** spécifique aux boissons (par 100ml)")

    # Option
    option = st.radio("Choisissez une option", 
                     ["Calculer pour un nouveau produit", "Tester avec la base de données"],
                     horizontal=True)
    
    if option == "Tester avec la base de données" and df is not None:
        st.info("""**Attention** : Il peut y avoir des différences entre le score de la BD et le score qui est affiché car OpenFoodFacts
        n'utilise pas l'algorithme spécifiquement pour les boissons comme nous l'avons fait""")
        produit_choisi = st.selectbox(
            "Sélectionnez un produit",
            df['Nom_Produit'].tolist(),
            index=6
        )
        
        produit = df[df['Nom_Produit'] == produit_choisi].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Informations produit")
            st.write(f"**Nom:** {produit['Nom_Produit']}")
            st.write(f"**Marque:** {produit['Marque']}")
            st.write(f"**Catégorie:** {produit['Categorie']}")
        
        with col2:
            st.markdown("#### Valeurs de référence")
            st.write(f"**Score BD:** {produit['Score_Nutriscore']}")
            st.write(f"**Label BD:** {produit['Label_Nutriscore']}")

        # Détection eau
        est_eau = produit['Categorie'].lower() == 'eau'

        # Détection édulcorants
        contient_edulcorants = False
        if pd.notna(produit['Liste_Additifs']):
            edulcorants_codes = ['e950', 'e951', 'e952', 'e954', 'e955', 'e960', 'e961']
            contient_edulcorants = any(code in str(produit['Liste_Additifs']).lower() 
                                      for code in edulcorants_codes)
        
        if st.button("Calculer le Nutri-Score", type="primary"):
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
            
            st.markdown("---")
            st.markdown("## Résultat du calcul")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown(
                    f"<div style='background-color: {resultat['couleur']}; "
                    f"padding: 40px; border-radius: 15px; text-align: center;'>"
                    f"<h1 style='color: white; margin: 0; font-size: 4rem;'>{resultat['label']}</h1>"
                    f"<p style='color: white; margin-top: 10px; font-size: 1.5rem;'>Score: {resultat['score']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("### Détails du calcul")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Composante Négative (N)")
                details = resultat['details']
                st.write(f"- Énergie: **{details['points_energie']}** points")
                st.write(f"- Acides gras saturés: **{details['points_acides_gras_satures']}** points")
                st.write(f"- Sucres: **{details['points_sucres']}** points")
                st.write(f"- Sel: **{details['points_sel']}** points")
                if contient_edulcorants:
                    st.write(f"- Édulcorants: **{details['points_edulcorants']}** points")
                st.write(f"**Total N = {details['score_negatif']}**")
            
            with col2:
                st.markdown("#### Composante Positive (P)")
                st.write(f"- Protéines: **{details['points_proteines']}** points")
                st.write(f"- Fibres: **{details['points_fibres']}** points")
                st.write(f"- Fruits/Légumes: **{details['points_fruits_legumes']}** points")
                st.write(f"**Total P = {details['score_positif']}** (max 7 pour boissons)")
            
            st.info(f"**Explication:** {details['explication']}")

            # Comparaison
            concordance = resultat['label'] == produit['Label_Nutriscore']
            if concordance:
                st.success(f"**Concordance parfaite !** Le calcul correspond au label de la base de données.")
            else:
                st.warning(f"Différence détectée : Calculé = {resultat['label']}, Base de données = {produit['Label_Nutriscore']}")

    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Composantes à limiter")
            energie_kj = st.number_input("Énergie (kJ/100ml)", 0.0, 500.0, 180.0)
            sucres = st.number_input("Sucres (g/100ml)", 0.0, 20.0, 10.6)
            acides_gras = st.number_input("Acides gras saturés (g/100ml)", 0.0, 5.0, 0.0)
            sel = st.number_input("Sel (g/100ml)", 0.0, 2.0, 0.0)
            contient_edulcorants = st.checkbox("Contient des édulcorants")
        
        with col2:
            st.markdown("### Composantes à favoriser")
            proteines = st.number_input("Protéines (g/100ml)", 0.0, 10.0, 0.0)
            fibres = st.number_input("Fibres (g/100ml)", 0.0, 10.0, 0.0)
            fruits_legumes = st.number_input("Fruits/Légumes (%)", 0, 100, 0)
            est_eau = st.checkbox("C'est de l'eau (automatiquement A)")
        
        if st.button("Calculer le Nutri-Score", type="primary"):
            resultat = NutriScoreBoissons.calculer_score_nutritionnel(
                energie_kj, acides_gras, sucres, sel, contient_edulcorants,
                proteines, fibres, fruits_legumes, est_eau
            )
            
            st.markdown("---")
            st.markdown("## Résultat")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown(
                    f"<div style='background-color: {resultat['couleur']}; "
                    f"padding: 40px; border-radius: 15px; text-align: center;'>"
                    f"<h1 style='color: white; margin: 0; font-size: 4rem;'>{resultat['label']}</h1>"
                    f"<p style='color: white; margin-top: 10px; font-size: 1.5rem;'>Score: {resultat['score']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )

# PAGE ELECTRE TRI
elif page == "ELECTRE TRI":
    st.markdown("## Classification ELECTRE TRI")
    st.info("Méthode de tri multicritère basée sur des profils de référence")
    
    if df is None:
        st.error("Impossible de charger la base de données")
    else:
        st.sidebar.markdown("### Paramètres ELECTRE TRI")
        
        methode = st.sidebar.radio("Procédure", ["Pessimiste", "Optimiste"])
        lambda_seuil = st.sidebar.slider("Seuil λ (concordance)", 0.5, 0.9, 0.6, 0.05)
        
        st.sidebar.markdown("### Poids des critères")
        poids_default = definir_poids_criteres()
        
        poids = {}
        criteres_noms = {
            'Energie_kJ': 'Énergie',
            'Acides_Gras_Satures_g': 'Acides gras saturés',
            'Sucres_g': 'Sucres',
            'Sel_g': 'Sel',
            'Proteines_g': 'Protéines',
            'Fibres_g': 'Fibres',
            'Fruits_Legumes_Pct': 'Fruits/Légumes',
            'Nombre_Additifs': 'Additifs'
        }

        for crit, nom in criteres_noms.items():
            poids[crit] = st.sidebar.slider(nom, 0.0, 0.5, poids_default[crit], 0.05)

        # Normalisation
        somme = sum(poids.values())
        if somme > 0:
            poids = {k: v/somme for k, v in poids.items()}
        
        st.sidebar.success(f"Somme normalisée: {sum(poids.values()):.2f}")
        
        if st.button("Lancer la classification", type="primary", use_container_width=True):
            with st.spinner("Classification en cours..."):
                profils = creer_profils_limites(df)
                
                st.markdown("### Profils limites (b1 à b6)")
                st.info("b6 = meilleur profil (A) | b1 = pire profil (E)")
                st.dataframe(profils.T.style.background_gradient(cmap='RdYlGn_r', axis=1),
                           use_container_width=True)
                
                electre = ElectreTri(poids, profils, lambda_seuil)
                df_resultat = electre.classifier_base_donnees(df, methode.lower())
                
                colonne_classe = f'Classe_ELECTRE_{methode}'
                
                st.markdown(f"### Résultats - Procédure {methode}")
                
                col1, col2 = st.columns([3, 2])

                with col1:
                    classes_count = df_resultat[colonne_classe].value_counts().sort_index()

                    # S'assurer d'avoir toutes les classes A-E (remplir avec 0 si manquantes)
                    all_classes = ['A', 'B', 'C', 'D', 'E']
                    classes_completes = pd.Series({c: classes_count.get(c, 0) for c in all_classes})

                    # Labels avec apostrophes pour l'affichage
                    labels_display = [f"{c}'" for c in all_classes]

                    fig = px.bar(
                        x=labels_display,
                        y=classes_completes.values,
                        labels={'x': 'Classe ELECTRE TRI', 'y': 'Nombre de produits'},
                        color=labels_display,
                        color_discrete_map={
                            "A'": '#038141', "B'": '#85BB2F', "C'": '#FECB02',
                            "D'": '#EE8100', "E'": '#E63E11'
                        },
                        text=classes_completes.values,
                        title=f"Distribution ELECTRE TRI - Procédure {methode}"
                    )
                    fig.update_traces(textposition='outside', textfont_size=14)
                    fig.update_layout(
                        showlegend=False,
                        height=450,
                        xaxis_title_font_size=14,
                        yaxis_title_font_size=14,
                        title_font_size=16
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### Statistiques")
                    for classe in classes_count.index:
                        pct = classes_count[classe] / len(df) * 100
                        st.metric(f"Classe {classe}'", f"{classes_count[classe]} ({pct:.1f}%)")
                
                st.markdown("### Comparaison avec Nutri-Score")
                
                df_comp = df_resultat.copy()
                df_comp['Classe_Clean'] = df_comp[colonne_classe].str.replace("'", "")
                
                matrice = AnalyseResultats.matrice_confusion(
                    df_comp['Label_Nutriscore'],
                    df_comp['Classe_Clean']
                )
                
                col1, col2 = st.columns([2, 1])
                
                matrice_prime = ["A'","B'","C'","D'","E'"]
                
                with col1:
                    fig_heatmap = px.imshow(
                        matrice.values,
                        labels=dict(x="ELECTRE TRI", y="Nutri-Score", color="Nombre"),
                        x=matrice_prime,
                        y=matrice.index,
                        color_continuous_scale='Blues',
                        text_auto=True
                    )
                    fig_heatmap.update_layout(height=400, title="Matrice de confusion")
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                
                with col2:
                    metriques = AnalyseResultats.calculer_metriques(matrice)
                    st.metric("Précision", f"{metriques['accuracy']:.1%}")

                    st.markdown("#### Métriques par classe")
                    for classe in ["A", "B", "C", "D", "E"]:
                        if classe in metriques['par_classe']:
                            m = metriques['par_classe'][classe]
                            with st.expander(f"Classe {classe}'"):
                                st.write(f"Précision: {m['precision']:.1%}")
                                st.write(f"Rappel: {m['rappel']:.1%}")
                                st.write(f"F1-Score: {m['f1_score']:.1%}")

# PAGE SUPERNUTRI-SCORE
elif page == "SuperNutri-Score":
    st.markdown("## SuperNutri-Score")
    st.info("Évaluation holistique combinant Nutri-Score + Green-Score + Label BIO")
    
    if df is None:
        st.error("Impossible de charger la base de données")
    else:
        st.sidebar.markdown("### Pondération des dimensions")
        poids_nutri = st.sidebar.slider("Nutri-Score", 0.0, 1.0, 0.5, 0.05)
        poids_green = st.sidebar.slider("Green-Score", 0.0, 1.0, 0.3, 0.05)
        poids_bio = st.sidebar.slider("Label BIO", 0.0, 1.0, 0.2, 0.05)

        # Normalisation
        total = poids_nutri + poids_green + poids_bio
        if total > 0:
            poids_nutri /= total
            poids_green /= total
            poids_bio /= total
        
        st.sidebar.success(f"Total: {poids_nutri + poids_green + poids_bio:.2f}")
        
        if st.button("Calculer le SuperNutri-Score", type="primary"):
            with st.spinner("Calcul en cours..."):
                resultats = []
                
                for idx, row in df.iterrows():
                    super_score = SuperNutriScore.calculer_super_score(
                        row['Label_Nutriscore'],
                        row['Label_Greenscore'] if pd.notna(row['Label_Greenscore']) else 'NOT-APPLICABLE',
                        row['Label_Bio'],
                        poids_nutri, poids_green, poids_bio
                    )
                    resultats.append({
                        'Nom_Produit': row['Nom_Produit'],
                        'SuperNutri_Score': super_score['score'],
                        'SuperNutri_Classe': super_score['classe']
                    })
                
                df_super = pd.DataFrame(resultats)
                df_final = df.merge(df_super, on='Nom_Produit')
                
                st.markdown("### Résultats SuperNutri-Score")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### Distribution SuperNutri-Score")
                    super_count = df_final['SuperNutri_Classe'].value_counts().sort_index()
                    
                    fig = px.bar(
                        labels=dict(x="SuperNutri-Score", y="Quantité", color="Nombre"),
                        x=super_count.index,
                        y=super_count.values,
                        color=super_count.index,
                        color_discrete_map={
                            'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02',
                            'D': '#EE8100', 'E': '#E63E11'
                        },
                        text=super_count.values
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(showlegend=False, height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### Distribution Nutri-Score")
                    nutri_count = df_final['Label_Nutriscore'].value_counts().sort_index()
                    
                    fig2 = px.bar(
                        labels=dict(x="Nutri-Score", y="Quantité", color="Nombre"),
                        x=nutri_count.index,
                        y=nutri_count.values,
                        color=nutri_count.index,
                        color_discrete_map={
                            'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02',
                            'D': '#EE8100', 'E': '#E63E11'
                        },
                        text=nutri_count.values
                    )
                    fig2.update_traces(textposition='outside')
                    fig2.update_layout(showlegend=False, height=500)
                    st.plotly_chart(fig2, use_container_width=True)
                
                with col3:
                    st.markdown("#### Statistiques")
                    avg_score = df_final['SuperNutri_Score'].mean()
                    st.metric("Score moyen", f"{avg_score:.2f}")
                    
                    meilleur = df_final.nsmallest(1, 'SuperNutri_Score').iloc[0]
                    st.success(f"Meilleur: {meilleur['Nom_Produit']}")
                    
                    pire = df_final.nlargest(1, 'SuperNutri_Score').iloc[0]
                    st.error(f"Pire: {pire['Nom_Produit']}")

                # Matrice
                st.markdown("### Comparaison SuperNutri-Score vs Nutri-Score")
                
                matrice_super = AnalyseResultats.matrice_confusion(
                    df_final['Label_Nutriscore'],
                    df_final['SuperNutri_Classe']
                )
                
                col1, col2 = st.columns([2, 1])
                matrice_prime = ["A'","B'","C'","D'","E'"]
                
                with col1:
                    fig_heat = px.imshow(
                        matrice_super.values,
                        labels=dict(x="SuperNutri-Score", y="Nutri-Score", color="Nombre"),
                        x=matrice_prime,
                        y=matrice_super.index,
                        color_continuous_scale='Viridis',
                        text_auto=True
                    )
                    fig_heat.update_layout(height=400)
                    st.plotly_chart(fig_heat, use_container_width=True)
                
                with col2:
                    metriques_super = AnalyseResultats.calculer_metriques(matrice_super)
                    st.metric("Concordance", f"{metriques_super['accuracy']:.1%}")

                # Tableau
                st.markdown("### Top 20 produits")
                colonnes = ['Nom_Produit', 'Marque', 'Label_Nutriscore', 
                           'Label_Greenscore', 'Label_Bio', 'SuperNutri_Classe', 'SuperNutri_Score']
                st.dataframe(
                    df_final[colonnes].sort_values('SuperNutri_Score').head(20),
                    use_container_width=True
                )

# PAGE ANALYSE COMPARATIVE
elif page == "Analyse Comparative":
    st.markdown("## Analyse Comparative Approfondie")
    
    if df is None:
        st.error("Impossible de charger la base de données")
    else:
        st.info("Comparaison des 3 méthodes avec différents paramètres")

        # Tests
        st.markdown("### Comparaison Nutri-Score vs ELECTRE TRI")
        
        with st.spinner("Calcul en cours..."):
            resultats_comp = []
            
            for lambda_val in [0.6, 0.7, 0.8]:
                for methode in ['pessimiste', 'optimiste']:
                    profils = creer_profils_limites(df)
                    poids = definir_poids_criteres()
                    
                    electre = ElectreTri(poids, profils, lambda_val)
                    df_temp = electre.classifier_base_donnees(df, methode)
                    
                    colonne = f'Classe_ELECTRE_{methode.capitalize()}'
                    matrice = AnalyseResultats.matrice_confusion(
                        df_temp['Label_Nutriscore'],
                        df_temp[colonne]
                    )
                    metriques = AnalyseResultats.calculer_metriques(matrice)
                    
                    resultats_comp.append({
                        'λ': lambda_val,
                        'Méthode': methode.capitalize(),
                        'Précision': metriques['accuracy']
                    })
            
            df_comp = pd.DataFrame(resultats_comp)

            # Graphique
            fig = px.bar(
                df_comp,
                x='Méthode',
                y='Précision',
                color='λ',
                barmode='group',
                title="Précision selon λ et la procédure",
                text=df_comp['Précision'].apply(lambda x: f"{x:.1%}")
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                df_comp.style.format({'Accuracy': '{:.1%}'}),
                use_container_width=True
            )

        # Analyse par catégorie
        st.markdown("### Analyse par catégorie de produits")
        
        top_categories = df['Categorie'].value_counts().head(5)
        
        for categorie in top_categories.index:
            with st.expander(f"{categorie} ({top_categories[categorie]} produits)"):
                df_cat = df[df['Categorie'] == categorie]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    labels_dist = df_cat['Label_Nutriscore'].value_counts().sort_index()
                    fig = px.pie(
                        values=labels_dist.values,
                        names=labels_dist.index,
                        title="Nutri-Score",
                        color=labels_dist.index,
                        color_discrete_map={
                            'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02',
                            'D': '#EE8100', 'E': '#E63E11'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    stats = df_cat[['Energie_kcal', 'Sucres_g', 'Proteines_g', 'Nombre_Additifs']].describe()
                    st.dataframe(stats.T, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 2rem;'>
    <p><strong>Projet Transparence des algorithmes</strong> - Mehdi TAZEROUTI, Salim BOUSKINE</p>
</div>
""", unsafe_allow_html=True)
