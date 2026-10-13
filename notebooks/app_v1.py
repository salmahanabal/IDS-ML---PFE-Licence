"""
=====================================================================
 Interface de Détection d'Intrusion Réseau - Random Forest (NSL-KDD)
=====================================================================
Cette application Streamlit permet d'uploader un fichier CSV DÉJÀ
PRÉTRAITÉ (122 colonnes, one-hot encoding déjà appliqué sur
protocol_type / service / flag, identique à X_train / X_test dans
le notebook), de prédire chaque ligne avec le modèle Random Forest
optimisé, puis de visualiser un résumé global des résultats sur
l'ensemble des vecteurs importés (un seul vecteur ou plusieurs
milliers en une seule fois).

Fichiers requis dans le même dossier que ce script :
    - rf_model.pkl       (modèle Random Forest entraîné, via joblib.dump)
    - rf_columns.pkl     (liste des colonnes attendues après one-hot encoding)
    - rf_threshold.pkl   (seuil de décision optimal trouvé dans le notebook)

Lancement :
    python -m streamlit run app_v1.py
=====================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
BASE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Détection d'intrusion - Random Forest",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Détection d'intrusion réseau (NSL-KDD)")
st.markdown(
    "Modèle utilisé : **Random Forest** "
    "(meilleur compromis accuracy / AUC / recall parmi les 3 modèles comparés "
    "dans l'étude — Random Forest, SVM, XGBoost). "
    "Le fichier importé doit être **déjà prétraité** (122 colonnes, one-hot "
    "encoding déjà appliqué), au même format que `X_train` / `X_test` dans le notebook."
)

# ---------------------------------------------------------------------------
# Chargement du modèle et des artefacts (mise en cache)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    model = joblib.load(BASE / "rf_model.pkl")
    columns = joblib.load(BASE / "rf_columns.pkl")
    threshold = joblib.load(BASE / "rf_threshold.pkl")
    return model, columns, threshold

try:
    rf_model, expected_columns, default_threshold = load_artifacts()
    st.sidebar.success("Modèle chargé avec succès ")
except FileNotFoundError:
    st.error(
        "Fichiers du modèle introuvables. Assure-toi que `rf_model.pkl`, "
        "`rf_columns.pkl` et `rf_threshold.pkl` sont dans le même dossier "
        "que ce script (générés depuis le notebook avec `joblib.dump`)."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Barre latérale : réglages
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Paramètres")

threshold = st.sidebar.slider(
    "Seuil de décision (probabilité d'attaque)",
    min_value=0.0,
    max_value=1.0,
    value=float(default_threshold),
    step=0.001,
    format="%.5f",
    help=(
        "Seuil optimal trouvé dans le notebook (maximise le F1-score sur "
        "la classe 'attack'). Ajustable pour explorer le compromis "
        "precision/recall."
    )
)

st.sidebar.markdown(f"**Seuil par défaut (notebook) :** `{default_threshold:.5f}`")
st.sidebar.markdown(f"**Colonnes attendues par le modèle :** `{len(expected_columns)}`")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "ℹ️ Le fichier CSV doit déjà être au format **prétraité** "
    "(122 colonnes), pas le format brut NSL-KDD à 41 colonnes."
)

# ---------------------------------------------------------------------------
# Upload du fichier CSV
# ---------------------------------------------------------------------------
st.header("📁 Importer un fichier de test (un ou plusieurs vecteurs)")

uploaded_file = st.file_uploader(
    "Choisis un fichier CSV déjà prétraité (122 colonnes)",
    type=["csv"]
)

if uploaded_file is None:
    st.info("⬆️ Importe un fichier CSV pour lancer la prédiction.")
    st.stop()

try:
    df_raw = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
    st.stop()

n_vectors = df_raw.shape[0]
st.subheader("Aperçu des données importées")
st.dataframe(df_raw.head(10), use_container_width=True)
st.caption(f"{n_vectors} vecteur(s) réseau importé(s), {df_raw.shape[1]} colonnes.")

# ---------------------------------------------------------------------------
# Vérification + alignement des colonnes (dataset déjà prétraité)
# ---------------------------------------------------------------------------
has_true_labels = "class" in df_raw.columns
y_true = None
if has_true_labels:
    y_true = (
        df_raw["class"]
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(lambda x: "normal" if x == "normal" else "attack")
    )

df_features = df_raw.drop(columns=["class"], errors="ignore")

missing_cols = [c for c in expected_columns if c not in df_features.columns]
if missing_cols:
    st.error(
        f"⚠️ {len(missing_cols)} colonne(s) attendue(s) par le modèle sont "
        f"absentes du fichier importé. Le fichier doit être déjà prétraité "
        f"(122 colonnes, one-hot encoding inclus). "
        f"Exemples de colonnes manquantes : {missing_cols[:5]}"
    )
    st.stop()

extra_cols = [c for c in df_features.columns if c not in expected_columns]
if extra_cols:
    st.warning(
        f"ℹ️ {len(extra_cols)} colonne(s) non reconnue(s) par le modèle "
        f"seront ignorées : {extra_cols[:5]}"
    )

# Réalignement strict sur l'ordre exact des colonnes utilisées à l'entraînement
df_encoded = df_features.reindex(columns=expected_columns, fill_value=0)

# ---------------------------------------------------------------------------
# Prédiction sur l'ensemble des vecteurs importés
# ---------------------------------------------------------------------------
attack_index = list(rf_model.classes_).index("attack")
y_score = rf_model.predict_proba(df_encoded)[:, attack_index]
y_pred = np.where(y_score >= threshold, "attack", "normal")

results_df = df_raw.copy()
results_df["probabilite_attack"] = y_score
results_df["prediction"] = y_pred

# ===========================================================================
# RÉSUMÉ GLOBAL — traite aussi bien 1 vecteur que plusieurs milliers
# ===========================================================================
st.header("→ Résumé global des prédictions")

n_total = len(results_df)
n_attack = int((y_pred == "attack").sum())
n_normal = int((y_pred == "normal").sum())
taux_attack = n_attack / n_total if n_total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vecteurs analysés", f"{n_total:,}")
col2.metric("🚨 Attaques détectées", f"{n_attack:,}", f"{taux_attack:.1%}")
col3.metric("✅ Connexions normales", f"{n_normal:,}", f"{1 - taux_attack:.1%}")
col4.metric("Probabilité moyenne d'attaque", f"{y_score.mean():.3f}")

# Barre de progression visuelle simple : proportion attack/normal
st.markdown("**Répartition globale :**")
st.progress(taux_attack)
st.caption(f"{taux_attack:.1%} des vecteurs importés sont classés comme attaque.")

# ---------------------------------------------------------------------------
# Tableau détaillé (toutes les lignes, avec mise en couleur)
# ---------------------------------------------------------------------------
st.subheader("Détail des prédictions par vecteur")

def highlight_attack(row):
    color = "background-color: #ffcccc" if row["prediction"] == "attack" else "background-color: #ccffcc"
    return [color] * len(row)

# Pour de gros volumes, on évite de styliser des milliers de lignes (lent) :
# on stylise seulement si le volume reste raisonnable.
if n_total <= 2000:
    st.dataframe(
        results_df.style.apply(highlight_attack, axis=1),
        use_container_width=True
    )
else:
    st.info(
        f"Affichage sans mise en couleur ({n_total:,} lignes — la mise en "
        f"couleur est désactivée au-delà de 2000 lignes pour rester fluide)."
    )
    st.dataframe(results_df, use_container_width=True)

csv_export = results_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Télécharger tous les résultats (CSV)",
    data=csv_export,
    file_name="resultats_predictions.csv",
    mime="text/csv"
)

# ---------------------------------------------------------------------------
# Visualisations globales (s'adaptent automatiquement au nombre de vecteurs)
# ---------------------------------------------------------------------------
st.header("📈 Visualisations globales")

viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.subheader("Répartition des prédictions")
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    counts = results_df["prediction"].value_counts().reindex(["normal", "attack"]).fillna(0)
    ax1.bar(counts.index, counts.values, color=["#2ca02c", "#d62728"])
    ax1.set_ylabel("Nombre de vecteurs")
    ax1.set_title(f"Normal vs Attack — {n_total:,} vecteurs analysés")
    for i, v in enumerate(counts.values):
        ax1.text(i, v + max(counts.values) * 0.01, f"{int(v):,}", ha="center", fontweight="bold")
    st.pyplot(fig1)

with viz_col2:
    st.subheader("Distribution des probabilités d'attaque")
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.hist(y_score, bins=min(30, max(5, n_total // 2)), color="steelblue", edgecolor="black", alpha=0.7)
    ax2.axvline(threshold, color="red", linestyle="--", label=f"Seuil = {threshold:.4f}")
    ax2.set_xlabel("Probabilité d'attaque")
    ax2.set_ylabel("Nombre de vecteurs")
    ax2.set_title("Distribution des scores sur tous les vecteurs")
    ax2.legend()
    st.pyplot(fig2)

# Camembert récapitulatif (utile en présentation/démo pour un coup d'œil rapide)
st.subheader("Vue d'ensemble (camembert)")
fig3, ax3 = plt.subplots(figsize=(4, 4))
ax3.pie(
    [n_normal, n_attack],
    labels=["Normal", "Attack"],
    autopct="%1.1f%%",
    colors=["#2ca02c", "#d62728"],
    startangle=90
)
ax3.set_title(f"Répartition sur {n_total:,} vecteurs")
st.pyplot(fig3)

# ---------------------------------------------------------------------------
# Évaluation si les vraies étiquettes sont disponibles dans le CSV
# ---------------------------------------------------------------------------
if has_true_labels:
    st.header("✅ Évaluation par rapport aux vraies étiquettes")
    st.caption(
        "La colonne `class` était présente dans le fichier importé : "
        "comparaison automatique prédiction vs réalité sur l'ensemble des vecteurs."
    )

    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

    accuracy = accuracy_score(y_true, y_pred)
    st.metric("Accuracy sur ce fichier", f"{accuracy:.2%}")

    eval_col1, eval_col2 = st.columns(2)

    with eval_col1:
        st.subheader("Rapport de classification")
        report = classification_report(y_true, y_pred, output_dict=True)
        st.dataframe(pd.DataFrame(report).transpose(), use_container_width=True)

    with eval_col2:
        st.subheader("Matrice de confusion")
        cm = confusion_matrix(y_true, y_pred, labels=["normal", "attack"])
        fig4, ax4 = plt.subplots(figsize=(5, 4))
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["normal", "attack"],
            yticklabels=["normal", "attack"],
            ax=ax4
        )
        ax4.set_xlabel("Prédiction")
        ax4.set_ylabel("Réel")
        st.pyplot(fig4)
else:
    st.info(
        "ℹ️ Aucune colonne `class` détectée dans le fichier importé — "
        "impossible de calculer une accuracy ou une matrice de confusion. "
        "Seules les prédictions sont affichées."
    )