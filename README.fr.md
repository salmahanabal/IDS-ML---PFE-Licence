🇬🇧 [Read in English](README.md)

# Détection d'intrusions réseau par Machine Learning (NSL-KDD)

Un projet de machine learning qui détecte les connexions réseau malveillantes. Il entraîne et compare trois classifieurs (SVM, Random Forest et XGBoost) sur le jeu de données de référence NSL-KDD, puis met le modèle retenu (Random Forest) à disposition à travers une petite interface web Streamlit : on y importe des enregistrements de trafic réseau et on obtient une prédiction pour chacun.

Ce travail est né comme projet de fin d'études (Licence en Sciences Mathématiques et Informatique, Faculté des Sciences de Rabat). Il est partagé ici comme un exemple complet et exécutable de chaîne de machine learning : préparation des données, comparaison de modèles, export du modèle, puis application simple par-dessus.

Le rapport complet du projet (61 pages) est disponible ici : [report/Rapport_PFE_IDS_NSL-KDD.pdf](report/Rapport_PFE_IDS_NSL-KDD.pdf).

## Ce que fait le projet

- Nettoie et prépare les données NSL-KDD (étiquettes binaires, encodage one-hot, alignement des colonnes entre entraînement et test).
- Entraîne trois modèles sur les mêmes données et les évalue sur le jeu de test officiel avec les mêmes métriques.
- Choisit un seuil de décision pour chaque modèle à partir de sa courbe précision-rappel, au lieu du seuil par défaut de 0,5.
- Sauvegarde le modèle Random Forest final, ses colonnes attendues et son seuil sur le disque.
- Propose une application Streamlit qui charge ces fichiers et classe les fichiers CSV importés en `normal` ou `attack`.

## Jeu de données

[NSL-KDD](https://www.kaggle.com/datasets/hassan06/nslkdd) est une version nettoyée du jeu KDD Cup 99, très utilisée pour évaluer les systèmes de détection d'intrusion. Chaque ligne décrit une connexion réseau avec 41 attributs (durée, protocole, service, octets transférés, taux d'erreur, etc.).

| Fichier | Lignes | Rôle |
| --- | --- | --- |
| `KDDTrain.csv` | 125 973 | Entraînement |
| `KDDTest.csv` | 22 544 | Test |

Les étiquettes d'origine (normal, DoS, Probe, R2L, U2R) sont regroupées en deux classes : `normal` et `attack`. Les trois attributs catégoriels (`protocol_type`, `service`, `flag`) sont encodés en one-hot, ce qui donne **122 colonnes d'entrée**. Le découpage officiel entraînement/test est conservé tel quel, sans nouveau découpage aléatoire.

## Résultats

Tous les chiffres ci-dessous sont mesurés sur les 22 544 connexions de `KDDTest.csv`, avec le seuil choisi pour chaque modèle. La classe `attack` est la classe positive.

| Modèle | Accuracy | Précision (attack) | Rappel (attack) | F1 (attack) | AUC |
| --- | --- | --- | --- | --- | --- |
| SVM (noyau RBF) | 87,13 % | 0,91 | 0,86 | 0,88 | 0,904 |
| Random Forest | **92,19 %** | 0,89 | 0,99 | 0,93 | 0,966 |
| XGBoost | 91,46 % | 0,88 | 0,99 | 0,93 | **0,970** |

Random Forest et XGBoost sont très proches et nettement devant le SVM. Random Forest a la meilleure accuracy et un peu moins de fausses alertes (1 585 contre 1 738), tandis que XGBoost a la meilleure AUC. Les deux laissent passer très peu d'attaques (175 et 187 attaques non détectées). Random Forest a été retenu pour l'interface.

Matrice de confusion (à gauche) et courbe ROC (à droite) du Random Forest :

<p>
  <img src="screenshots/rf_confusion_matrix.png" width="45%" alt="Matrice de confusion du Random Forest">
  <img src="screenshots/rf_roc_curve.png" width="45%" alt="Courbe ROC du Random Forest">
</p>

### Paramètres des modèles

- **SVM :** `StandardScaler` suivi de `SVC` (noyau RBF, `C=1.0`, `gamma='scale'`, `probability=True`).
- **Random Forest :** 500 arbres, `max_depth=15`, `min_samples_split=10`, `min_samples_leaf=4`, `max_features='sqrt'`.
- **XGBoost :** 500 arbres, `max_depth=8`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.1`, `reg_lambda=1.0`.

## L'interface web

L'application (`notebooks/app_v1.py`) permet de :

- importer un fichier CSV contenant un ou plusieurs enregistrements réseau ;
- ajuster le seuil de décision avec un curseur dans la barre latérale (la valeur par défaut est celle enregistrée par le notebook) ;
- voir un résumé global (nombre d'enregistrements, attaques détectées, connexions normales, probabilité moyenne d'attaque) ;
- parcourir un tableau où chaque ligne est colorée selon sa prédiction, et télécharger les résultats en CSV ;
- afficher trois graphiques : effectifs par classe, distribution des probabilités d'attaque avec le seuil, et diagramme circulaire de la répartition ;
- si le fichier contient une colonne `class`, comparer les prédictions aux vraies étiquettes.

![Résumé de l'interface](screenshots/interface_summary.png)

![Graphiques de l'interface](screenshots/interface_charts.png)

**Format d'entrée.** L'application attend un fichier **déjà prétraité** : les 122 colonnes obtenues après l'encodage one-hot, au même format que `X_train` / `X_test` dans le notebook. Les colonnes manquantes déclenchent un avertissement et les colonnes en trop sont ignorées. Des exemples prêts à l'emploi sont fournis dans le dépôt :

- `notebooks/deux_lignes.csv` : deux enregistrements, un normal et une attaque ;
- `notebooks/ligne_attack_nslkdd.csv` et `notebooks/ligne_normal_nslkdd_corrige.csv` : un enregistrement chacun ;
- `APP_data_test/` : d'autres fichiers de test, dont `test_ready_for_interface.csv`.

## Structure du projet

```
.
├── notebooks/
│   ├── machine_learning_project.ipynb   # préparation, entraînement, évaluation, export du modèle
│   ├── app_v1.py                        # interface Streamlit
│   ├── KDDTrain.csv / KDDTest.csv       # données NSL-KDD
│   ├── rf_model.pkl                     # Random Forest entraîné
│   ├── rf_columns.pkl                   # les 122 colonnes attendues par le modèle
│   ├── rf_threshold.pkl                 # seuil de décision
│   ├── deux_lignes.csv, ligne_*.csv     # petits exemples pour l'application
│   └── req1.txt                         # dépendances Python
├── APP_data_test/                       # fichiers de test supplémentaires pour l'interface
├── data/                                # fichiers NSL-KDD d'origine
├── screenshots/                         # images utilisées dans ce README
└── .gitignore
```

## Démarrage

### 1. Installation

Il faut Python 3.10 ou plus récent.

```bash
git clone https://github.com/salmahanabal/IDS-ML---PFE-Licence.git
cd IDS-ML---PFE-Licence

python -m venv .venv
# Windows (PowerShell) :  .venv\Scripts\Activate.ps1
# macOS / Linux :         source .venv/bin/activate

pip install -r notebooks/req1.txt
pip install streamlit
```

### 2. Lancer l'interface

Les fichiers du modèle entraîné sont déjà dans le dépôt, vous pouvez donc lancer l'application tout de suite :

```bash
streamlit run notebooks/app_v1.py
```

Ouvrez ensuite l'adresse affichée dans le terminal (en général http://localhost:8501) et importez l'un des fichiers CSV d'exemple.

### 3. Reproduire l'entraînement

Ouvrez `notebooks/machine_learning_project.ipynb` dans Jupyter ou VS Code et exécutez les cellules de haut en bas, une seule fois. Le notebook lit `KDDTrain.csv` et `KDDTest.csv` dans son propre dossier et réécrit les trois fichiers `rf_*.pkl` à la fin de la cellule du Random Forest. L'entraînement peut être long, surtout le SVM avec estimation des probabilités et les courbes d'apprentissage par validation croisée : prévoyez du temps sur un ordinateur portable.

## Limites

- Le seuil de décision de chaque modèle est choisi à partir de la courbe précision-rappel calculée sur le jeu de test, qui est aussi celui utilisé pour présenter les métriques. Les scores indiqués sont donc un peu optimistes ; un protocole plus rigoureux choisirait le seuil sur un jeu de validation séparé.
- La tâche est binaire (`normal` ou `attack`) : elle n'indique pas le type d'attaque détecté.
- NSL-KDD est un jeu de référence de 2009. Il est utile pour comparer des méthodes, mais il ne reflète pas le trafic réseau actuel.
- L'interface exige des données prétraitées et n'est pas reliée à du trafic réseau en direct.

## Pistes d'amélioration

- Classification multi-classes pour identifier le type d'attaque (DoS, Probe, R2L, U2R), ce qui demande une stratégie pour les classes rares.
- Évaluer les modèles sur un jeu de données plus récent comme CICIDS2017.
- Intégrer le prétraitement dans l'application pour pouvoir importer directement des fichiers NSL-KDD bruts.
- Détection en temps réel sur des flux réseau capturés.

## Technologies

Python, pandas, NumPy, scikit-learn, XGBoost, matplotlib, seaborn, joblib, Streamlit, Jupyter.

## Auteurs

- **Salma Hanabal** : [@salmahanabal](https://github.com/salmahanabal)
- **Iliass El Khabbaoui** : [@ivanelk7](https://github.com/ivanelk7)
