import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional


class NutriScoreBoissons:
    # Tables de points (par 100ml)
    ENERGIE_POINTS = [
        (30, 0), (60, 1), (90, 2), (120, 3), (150, 4),
        (180, 5), (210, 6), (240, 7), (270, 8), (300, 9),
        (330, 10), (360, 11), (390, 12), (float('inf'), 13)
    ]
    
    SUCRES_POINTS = [
        (0.5, 0), (1.5, 1), (2.5, 2), (3.5, 3), (4.5, 4),
        (5.5, 5), (6.5, 6), (7.5, 7), (8.5, 8), (9.5, 9),
        (10.5, 10), (11, 11), (float('inf'), 12)
    ]
    
    ACIDES_GRAS_SATURES_POINTS = [
        (0.1, 0), (0.2, 1), (0.3, 2), (0.4, 3), (0.5, 4),
        (0.6, 5), (0.7, 6), (0.8, 7), (0.9, 8), (1.0, 9),
        (float('inf'), 10)
    ]
    
    SEL_POINTS = [
        (0.09, 0), (0.18, 1), (0.27, 2), (0.36, 3), (0.45, 4),
        (0.54, 5), (0.63, 6), (0.72, 7), (0.81, 8), (0.90, 9),
        (float('inf'), 10)
    ]
    
    POINTS_EDULCORANTS = 4  # Pénalité pour édulcorants

    # Composante POSITIVE (P)
    PROTEINES_POINTS = [
        (0.8, 0), (1.6, 1), (2.4, 2), (3.2, 3), (4.0, 4),
        (float('inf'), 5)
    ]
    
    FIBRES_POINTS = [
        (0.7, 0), (1.4, 1), (2.1, 2), (2.8, 3), (3.5, 4),
        (float('inf'), 5)
    ]
    
    FRUITS_LEGUMES_POINTS = [
        (40, 0), (60, 2), (80, 4), (float('inf'), 5)
    ]
    
    MAX_POINTS_P = 7

    # Classes Nutri-Score BOISSONS
    CLASSES_BOISSONS = [
        (-float('inf'), -2, 'A', '#038141'),
        (-1, 2, 'B', '#85BB2F'),
        (3, 6, 'C', '#FECB02'),
        (7, 9, 'D', '#EE8100'),
        (10, float('inf'), 'E', '#E63E11')
    ]
    
    @staticmethod
    def get_points(valeur: float, table: List[Tuple]) -> int:
        for seuil, points in table:
            if valeur < seuil:
                return points
        return table[-1][1]

    @classmethod
    def calculer_score_nutritionnel(cls,
                                   energie_kj: float,
                                   acides_gras_satures: float,
                                   sucres: float,
                                   sel: float,
                                   contient_edulcorants: bool,
                                   proteines: float,
                                   fibres: float,
                                   fruits_legumes: float,
                                   est_eau: bool = False) -> Dict:

        # Cas spécial : eau → automatiquement A
        if est_eau:
            return {
                'score': -10,
                'label': 'A',
                'couleur': '#038141',
                'details': {
                    'est_eau': True,
                    'score_negatif': 0,
                    'score_positif': 0,
                    'explication': "Les eaux sont automatiquement classées A"
                }
            }

        # Composante négative (N)
        points_energie = cls.get_points(energie_kj, cls.ENERGIE_POINTS)
        points_ag_sat = cls.get_points(acides_gras_satures, cls.ACIDES_GRAS_SATURES_POINTS)
        points_sucres = cls.get_points(sucres, cls.SUCRES_POINTS)
        points_sel = cls.get_points(sel, cls.SEL_POINTS)
        points_edulcorants = cls.POINTS_EDULCORANTS if contient_edulcorants else 0
        
        score_negatif = (points_energie + points_ag_sat + points_sucres +
                        points_sel + points_edulcorants)

        # Composante positive (P)
        points_proteines = cls.get_points(proteines, cls.PROTEINES_POINTS)
        points_fibres = cls.get_points(fibres, cls.FIBRES_POINTS)
        points_fruits_legumes = cls.get_points(fruits_legumes, cls.FRUITS_LEGUMES_POINTS)
        
        score_positif = min(
            points_proteines + points_fibres + points_fruits_legumes,
            cls.MAX_POINTS_P
        )

        # Score final = N - P
        score_final = score_negatif - score_positif

        # Détermination classe
        label = 'E'
        couleur = '#E63E11'
        
        for min_val, max_val, classe, coul in cls.CLASSES_BOISSONS:
            if min_val <= score_final <= max_val:
                label = classe
                couleur = coul
                break
        
        return {
            'score': score_final,
            'label': label,
            'couleur': couleur,
            'details': {
                'est_eau': False,
                'score_negatif': score_negatif,
                'score_positif': score_positif,
                'points_energie': points_energie,
                'points_acides_gras_satures': points_ag_sat,
                'points_sucres': points_sucres,
                'points_sel': points_sel,
                'points_edulcorants': points_edulcorants,
                'points_proteines': points_proteines,
                'points_fibres': points_fibres,
                'points_fruits_legumes': points_fruits_legumes,
                'explication': f"Score = N({score_negatif}) - P({score_positif}) = {score_final}"
            }
        }


class ElectreTri:

    def __init__(self, poids: Dict[str, float], profils: pd.DataFrame, lambda_seuil: float = 0.6):
        self.poids = poids
        self.profils = profils
        self.lambda_seuil = lambda_seuil

        self.criteres_a_minimiser = [
            'Energie_kJ', 'Acides_Gras_Satures_g',
            'Sucres_g', 'Sel_g', 'Nombre_Additifs'
        ]
        self.criteres_a_maximiser = [
            'Proteines_g', 'Fibres_g', 'Fruits_Legumes_Pct'
        ]

    def concordance_partielle(self, aliment: pd.Series, profil: pd.Series, critere: str) -> Tuple[float, float]:
        val_aliment = aliment[critere]
        val_profil = profil[critere]
        
        if critere in self.criteres_a_maximiser:
            c_ab = 1.0 if val_aliment >= val_profil else 0.0
            c_ba = 1.0 if val_profil >= val_aliment else 0.0
        else:
            c_ab = 1.0 if val_profil >= val_aliment else 0.0
            c_ba = 1.0 if val_aliment >= val_profil else 0.0
        
        return c_ab, c_ba

    def concordance_globale(self, aliment: pd.Series, profil: pd.Series) -> Tuple[float, float]:
        somme_poids = sum(self.poids.values())
        C_ab = 0.0
        C_ba = 0.0
        
        for critere, poids in self.poids.items():
            c_ab, c_ba = self.concordance_partielle(aliment, profil, critere)
            C_ab += poids * c_ab
            C_ba += poids * c_ba
        
        return C_ab / somme_poids, C_ba / somme_poids

    def surclassement(self, aliment: pd.Series, profil: pd.Series) -> Tuple[bool, bool]:
        C_ab, C_ba = self.concordance_globale(aliment, profil)
        return C_ab >= self.lambda_seuil, C_ba >= self.lambda_seuil

    def affectation_pessimiste(self, aliment: pd.Series) -> str:
        # Procédure pessimiste : compare de b6 à b1
        for i in range(6, 0, -1):
            profil = self.profils.loc[f'b{i}']
            a_S_b, b_S_a = self.surclassement(aliment, profil)
            
            if a_S_b:
                return {6: 'A', 5: 'B', 4: 'C', 3: 'D', 2: 'E', 1: 'E'}[i]
        return 'E'

    def affectation_optimiste(self, aliment: pd.Series) -> str:
        # Procédure optimiste : compare de b1 à b6
        for i in range(1, 7):
            profil = self.profils.loc[f'b{i}']
            a_S_b, b_S_a = self.surclassement(aliment, profil)
            
            if b_S_a and not a_S_b:
                return {1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'A'}[i]
        return 'A'

    def classifier_base_donnees(self, df: pd.DataFrame, methode: str = 'pessimiste') -> pd.DataFrame:
        resultats = []
        for idx, aliment in df.iterrows():
            if methode == 'pessimiste':
                classe = self.affectation_pessimiste(aliment)
            else:
                classe = self.affectation_optimiste(aliment)
            resultats.append(classe)
        
        df_resultat = df.copy()
        df_resultat[f'Classe_ELECTRE_{methode.capitalize()}'] = resultats
        return df_resultat


class SuperNutriScore:

    @staticmethod
    def normaliser_score(score: int, min_val: int, max_val: int) -> float:
        if max_val == min_val:
            return 0.0
        return (score - min_val) / (max_val - min_val)
    
    @classmethod
    def calculer_super_score(cls, nutriscore: str, greenscore: str, label_bio: str,
                            poids_nutri: float = 0.5, poids_green: float = 0.3,
                            poids_bio: float = 0.2) -> Dict:

        nutri_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
        green_mapping = {'A-PLUS': 0, 'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'NOT-APPLICABLE': 3}
        bio_mapping = {'OUI': 0, 'NON': 1}
        
        score_nutri = nutri_mapping.get(nutriscore, 4)
        score_green = green_mapping.get(greenscore, 3)
        score_bio = bio_mapping.get(label_bio, 1)
        
        nutri_norm = cls.normaliser_score(score_nutri, 0, 4)
        green_norm = cls.normaliser_score(score_green, 0, 6)
        bio_norm = score_bio
        
        score_final = (poids_nutri * nutri_norm + poids_green * green_norm + poids_bio * bio_norm)
        
        if score_final <= 0.2:
            classe, couleur = 'A', '#038141'
        elif score_final <= 0.4:
            classe, couleur = 'B', '#85BB2F'
        elif score_final <= 0.6:
            classe, couleur = 'C', '#FECB02'
        elif score_final <= 0.8:
            classe, couleur = 'D', '#EE8100'
        else:
            classe, couleur = 'E', '#E63E11'
        
        return {
            'score': score_final,
            'classe': classe,
            'couleur': couleur,
            'details': {
                'nutriscore': nutriscore,
                'score_nutri_norm': nutri_norm,
                'greenscore': greenscore,
                'score_green_norm': green_norm,
                'label_bio': label_bio,
                'score_bio_norm': bio_norm,
                'poids': {'nutri': poids_nutri, 'green': poids_green, 'bio': poids_bio}
            }
        }


class AnalyseResultats:

    @staticmethod
    def matrice_confusion(vraies_classes: pd.Series, classes_predites: pd.Series) -> pd.DataFrame:
        classes = ['A', 'B', 'C', 'D', 'E']
        matrice = pd.DataFrame(0, index=classes, columns=classes)
        
        for vrai, pred in zip(vraies_classes, classes_predites):
            vrai_clean = str(vrai).replace("'", "").strip()
            pred_clean = str(pred).replace("'", "").strip()
            
            if vrai_clean in classes and pred_clean in classes:
                matrice.loc[vrai_clean, pred_clean] += 1
        
        return matrice

    @staticmethod
    def calculer_metriques(matrice: pd.DataFrame) -> Dict:
        total = matrice.sum().sum()
        correct = np.trace(matrice)
        accuracy = correct / total if total > 0 else 0
        
        metriques_par_classe = {}
        for classe in matrice.index:
            tp = matrice.loc[classe, classe]
            fp = matrice[classe].sum() - tp
            fn = matrice.loc[classe].sum() - tp
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            rappel = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * rappel) / (precision + rappel) if (precision + rappel) > 0 else 0
            
            metriques_par_classe[classe] = {
                'precision': precision,
                'rappel': rappel,
                'f1_score': f1
            }
        
        return {'accuracy': accuracy, 'par_classe': metriques_par_classe}


def creer_profils_limites(df: pd.DataFrame) -> pd.DataFrame:
    # Création des 6 profils limites (b1 à b6) basés sur les quantiles
    criteres = ['Energie_kJ', 'Acides_Gras_Satures_g', 'Sucres_g', 'Sel_g',
                'Proteines_g', 'Fibres_g', 'Fruits_Legumes_Pct', 'Nombre_Additifs']
    
    profils = pd.DataFrame(index=['b1', 'b2', 'b3', 'b4', 'b5', 'b6'], columns=criteres)
    
    criteres_minimiser = ['Energie_kJ', 'Acides_Gras_Satures_g', 'Sucres_g', 'Sel_g', 'Nombre_Additifs']
    criteres_maximiser = ['Proteines_g', 'Fibres_g', 'Fruits_Legumes_Pct']
    
    for critere in criteres:
        if critere in criteres_minimiser:
            profils.loc['b6', critere] = df[critere].quantile(0.05)
            profils.loc['b5', critere] = df[critere].quantile(0.20)
            profils.loc['b4', critere] = df[critere].quantile(0.40)
            profils.loc['b3', critere] = df[critere].quantile(0.60)
            profils.loc['b2', critere] = df[critere].quantile(0.80)
            profils.loc['b1', critere] = df[critere].quantile(0.95)
        else:
            profils.loc['b6', critere] = df[critere].quantile(0.95)
            profils.loc['b5', critere] = df[critere].quantile(0.80)
            profils.loc['b4', critere] = df[critere].quantile(0.60)
            profils.loc['b3', critere] = df[critere].quantile(0.40)
            profils.loc['b2', critere] = df[critere].quantile(0.20)
            profils.loc['b1', critere] = df[critere].quantile(0.05)
    
    return profils.astype(float)


def definir_poids_criteres() -> Dict[str, float]:
    return {
        'Energie_kJ': 0.15,
        'Acides_Gras_Satures_g': 0.10,
        'Sucres_g': 0.20,
        'Sel_g': 0.10,
        'Proteines_g': 0.10,
        'Fibres_g': 0.10,
        'Fruits_Legumes_Pct': 0.15,
        'Nombre_Additifs': 0.10
    }
