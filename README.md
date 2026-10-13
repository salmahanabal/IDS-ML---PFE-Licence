<div align="center">

# Network Intrusion Detection
### with Machine Learning

<p>Detect malicious network connections with machine learning. Three classifiers are trained and compared on the NSL-KDD benchmark, and the selected Random Forest is served through an interactive Streamlit interface.</p>

<p>
  <a href="report/Rapport_PFE_IDS_NSL-KDD.pdf"><img src="https://img.shields.io/badge/See_the_report-1565C0?style=for-the-badge&logo=readthedocs&logoColor=white" alt="See the report"></a>
  <a href="README.fr.md"><img src="https://img.shields.io/badge/Version_fran%C3%A7aise-6A1B9A?style=for-the-badge&logo=googletranslate&logoColor=white" alt="Version française"></a>
</p>

<p>
  <a href="#results"><img src="https://img.shields.io/badge/Accuracy_92.19%25-2E7D32?style=for-the-badge" alt="Accuracy 92.19%"></a> <a href="#results"><img src="https://img.shields.io/badge/AUC_0.97-1565C0?style=for-the-badge" alt="AUC 0.97"></a> <a href="https://www.kaggle.com/datasets/hassan06/nslkdd"><img src="https://img.shields.io/badge/Dataset_NSL--KDD-455A64?style=for-the-badge" alt="Dataset NSL-KDD"></a>
</p>

<p>
  <a href="https://scikit-learn.org/stable/modules/svm.html"><img src="https://img.shields.io/badge/SVM-5E35B1?style=for-the-badge" alt="SVM"></a> <a href="https://scikit-learn.org/stable/modules/ensemble.html#forest"><img src="https://img.shields.io/badge/Random_Forest-2E7D32?style=for-the-badge" alt="Random Forest"></a> <a href="https://xgboost.readthedocs.io/"><img src="https://img.shields.io/badge/XGBoost-EF6C00?style=for-the-badge" alt="XGBoost"></a>
</p>

<p>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> <a href="https://scikit-learn.org/"><img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="scikit-learn"></a> <a href="https://pandas.pydata.org/"><img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="pandas"></a> <a href="https://numpy.org/"><img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy"></a> <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"></a> <a href="https://jupyter.org/"><img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter"></a>
</p>

</div>

---

## Table of contents

- [Overview](#overview)
- [Highlights](#highlights)
- [Dataset](#dataset)
- [Results](#results)
- [Web interface](#web-interface)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Limitations](#limitations)
- [Ideas for improvement](#ideas-for-improvement)
- [Authors](#authors)

---

## Overview

This project detects malicious network connections using machine learning. It trains and compares three classifiers (SVM, Random Forest and XGBoost) on the NSL-KDD benchmark dataset, then serves the selected model (Random Forest) through a small Streamlit web interface: you upload network traffic records and get a prediction for each one.

It started as an end-of-studies project (Licence in Mathematical Sciences and Computer Science, Faculty of Sciences, Rabat) and is shared here as a complete, runnable example of a machine learning pipeline. The full report (in French, 61 pages) is available [here](report/Rapport_PFE_IDS_NSL-KDD.pdf).

## Highlights

- Cleans and prepares the NSL-KDD data (binary labels, one-hot encoding, column alignment between train and test).
- Trains three models on the same data and evaluates them on the official test set with the same metrics.
- Chooses a decision threshold for each model from its precision-recall curve instead of using the default 0.5.
- Saves the final Random Forest model, its expected columns and its threshold to disk.
- Provides a Streamlit app that loads these files and classifies uploaded CSV files as `normal` or `attack`.

## Dataset

[NSL-KDD](https://www.kaggle.com/datasets/hassan06/nslkdd) is a cleaned-up version of the KDD Cup 99 dataset, widely used to evaluate intrusion detection systems. Each row describes one network connection with 41 features (duration, protocol, service, bytes transferred, error rates, and so on).

| File | Rows | Role |
| --- | --- | --- |
| `KDDTrain.csv` | 125,973 | Training |
| `KDDTest.csv` | 22,544 | Testing |

The original labels (normal, DoS, Probe, R2L, U2R) are grouped into two classes: `normal` and `attack`. The three categorical features (`protocol_type`, `service`, `flag`) are one-hot encoded, which gives **122 input columns**. The official train/test split is kept as is, with no random re-split.

## Results

All figures below are measured on the 22,544 connections of `KDDTest.csv`, at each model's chosen threshold. The `attack` class is the positive class.

| Model | Accuracy | Precision (attack) | Recall (attack) | F1 (attack) | AUC |
| --- | --- | --- | --- | --- | --- |
| SVM (RBF kernel) | 87.13 % | 0.91 | 0.86 | 0.88 | 0.904 |
| Random Forest | **92.19 %** | 0.89 | 0.99 | 0.93 | 0.966 |
| XGBoost | 91.46 % | 0.88 | 0.99 | 0.93 | **0.970** |

Random Forest and XGBoost are very close and clearly ahead of the SVM. Random Forest has the best accuracy and slightly fewer false alarms (1,585 against 1,738), while XGBoost has the best AUC. Both miss very few attacks (175 and 187 undetected attacks). Random Forest was kept for the interface.

Random Forest confusion matrix (left) and ROC curve (right):

<p align="center">
  <img src="screenshots/rf_confusion_matrix.png" width="45%" alt="Random Forest confusion matrix">
  <img src="screenshots/rf_roc_curve.png" width="45%" alt="Random Forest ROC curve">
</p>

<details>
<summary><strong>Model settings</strong></summary>

- **SVM:** `StandardScaler` followed by `SVC` (RBF kernel, `C=1.0`, `gamma='scale'`, `probability=True`).
- **Random Forest:** 500 trees, `max_depth=15`, `min_samples_split=10`, `min_samples_leaf=4`, `max_features='sqrt'`.
- **XGBoost:** 500 trees, `max_depth=8`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.1`, `reg_lambda=1.0`.

</details>

## The web interface

The app (`notebooks/app_v1.py`) lets you:

- upload a CSV file with one or several network records;
- adjust the decision threshold with a slider in the sidebar (the default is the one saved by the notebook);
- see a global summary (number of records, attacks detected, normal connections, mean attack probability);
- browse a table where each row is colored by its prediction, and download the results as CSV;
- view three charts: counts per class, distribution of attack probabilities with the threshold, and a pie chart of the split;
- if the file contains a `class` column, compare the predictions with the true labels.

<p align="center"><img src="screenshots/interface_summary.png" width="90%" alt="Interface summary"></p>

<p align="center"><img src="screenshots/interface_charts.png" width="90%" alt="Interface charts"></p>

**Input format.** The app expects a file that is **already preprocessed**: the 122 columns obtained after one-hot encoding, in the same format as `X_train` / `X_test` in the notebook. Missing columns trigger a warning, and extra columns are ignored. Ready-to-use examples are provided in the repository:

- `notebooks/deux_lignes.csv`: two records, one normal and one attack;
- `notebooks/ligne_attack_nslkdd.csv` and `notebooks/ligne_normal_nslkdd_corrige.csv`: one record each;
- `APP_data_test/`: further test files, including `test_ready_for_interface.csv`.

## Project structure

```
.
├── notebooks/
│   ├── machine_learning_project.ipynb   # data prep, training, evaluation, model export
│   ├── app_v1.py                        # Streamlit interface
│   ├── KDDTrain.csv / KDDTest.csv       # NSL-KDD data
│   ├── rf_model.pkl                     # trained Random Forest
│   ├── rf_columns.pkl                   # the 122 columns expected by the model
│   ├── rf_threshold.pkl                 # decision threshold
│   ├── deux_lignes.csv, ligne_*.csv     # small sample inputs for the app
│   └── req1.txt                         # Python dependencies
├── APP_data_test/                       # extra test files for the interface
├── data/                                # original NSL-KDD files
├── report/                              # full project report (PDF)
├── screenshots/                         # images used in this README
└── .gitignore
```

## Getting started

### 1. Install

You need Python 3.10 or newer.

```bash
git clone https://github.com/salmahanabal/IDS-ML---PFE-Licence.git
cd IDS-ML---PFE-Licence

python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# macOS / Linux:         source .venv/bin/activate

pip install -r notebooks/req1.txt
pip install streamlit
```

### 2. Run the interface

The trained model files are already in the repository, so you can launch the app right away:

```bash
streamlit run notebooks/app_v1.py
```

Then open the address shown in the terminal (usually http://localhost:8501) and upload one of the sample CSV files.

### 3. Reproduce the training

Open `notebooks/machine_learning_project.ipynb` in Jupyter or VS Code and run the cells from top to bottom, once. The notebook reads `KDDTrain.csv` and `KDDTest.csv` from its own folder and rewrites the three `rf_*.pkl` files at the end of the Random Forest cell. Training can be slow, especially the SVM with probability estimates and the cross-validated learning curves, so expect it to take a while on a laptop.

## Limitations

- The decision threshold of each model is chosen from the precision-recall curve computed on the test set, which is also the set used to report the metrics. The reported scores are therefore somewhat optimistic; a fairer protocol would pick the threshold on a validation split.
- The task is binary (`normal` or `attack`). It does not say which type of attack was detected.
- NSL-KDD is a 2009 benchmark. It is useful for comparing methods, but it does not reflect modern network traffic.
- The interface needs preprocessed input and is not connected to live network traffic.

## Ideas for improvement

- Multi-class classification to identify the type of attack (DoS, Probe, R2L, U2R), which needs a strategy for the rare classes.
- Evaluating the models on a more recent dataset such as CICIDS2017.
- Putting the preprocessing inside the app so that raw NSL-KDD files can be uploaded directly.
- Real-time detection on captured network flows.

## Tech stack

Python, pandas, NumPy, scikit-learn, XGBoost, matplotlib, seaborn, joblib, Streamlit, Jupyter.

## Authors

<table>
  <tr>
    <td align="center"><a href="https://github.com/salmahanabal"><b>Salma Hanabal</b></a><br><sub>@salmahanabal</sub></td>
    <td align="center"><a href="https://github.com/ivanelk7"><b>Iliass El Khabbaoui</b></a><br><sub>@ivanelk7</sub></td>
  </tr>
</table>
