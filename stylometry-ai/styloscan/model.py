"""Voie supervisée : Random Forest + validation croisée + importance de Gini.

Réplique fidèlement le pipeline du chapitre de référence, transposé à la
tâche « humain vs IA » :

  features interprétables  →  vecteurs n-dimensionnels  →  Random Forest
  →  validation croisée 5 plis  →  accuracy + F1  →  importance de Gini
  (+ PCA pour la visualisation, comme les case studies 3-4).

À utiliser dès qu'un corpus étiqueté est disponible. Tant qu'il ne l'est
pas, le scoring heuristique (scoring.py) prend le relais.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict

import numpy as np

from .features import FEATURE_NAMES, extract_features


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def load_corpus(corpus_dir: str, language: str | None = None):
    """Charge un corpus organisé en sous-dossiers par classe.

        corpus_dir/
          human/  *.txt
          ai/     *.txt        (ou gpt/, claude/, ... pour le multi-classe)

    Renvoie (X, y, labels, paths).
    """
    X, y, paths = [], [], []
    classes = sorted(d for d in os.listdir(corpus_dir)
                     if os.path.isdir(os.path.join(corpus_dir, d)))
    if not classes:
        raise ValueError(f"Aucun sous-dossier de classe dans {corpus_dir}")
    for cls in classes:
        cdir = os.path.join(corpus_dir, cls)
        for name in os.listdir(cdir):
            if not name.lower().endswith((".txt", ".md")):
                continue
            p = os.path.join(cdir, name)
            fr = extract_features(_read_text(p), language=language)
            X.append([fr.features.get(n, 0.0) for n in FEATURE_NAMES])
            y.append(cls)
            paths.append(p)
    return np.asarray(X, dtype=float), np.asarray(y), classes, paths


@dataclass
class TrainResult:
    classes: list
    n_samples: int
    accuracy_mean: float
    accuracy_sd: float
    f1_macro_mean: float
    f1_macro_sd: float
    gini_importance: list   # [(feature, importance)] décroissant
    per_class_f1: dict

    def summary(self) -> str:
        lines = [
            f"Échantillons : {self.n_samples}  | classes : {', '.join(self.classes)}",
            f"Accuracy (CV 5 plis) : {self.accuracy_mean:.1f}% ± {self.accuracy_sd:.1f}",
            f"F1 macro   (CV 5 plis) : {self.f1_macro_mean:.1f}% ± {self.f1_macro_sd:.1f}",
            "F1 par classe : " + ", ".join(f"{k} {v:.1f}%" for k, v in self.per_class_f1.items()),
            "Top features (importance de Gini) :",
        ]
        for feat, imp in self.gini_importance[:12]:
            lines.append(f"   {imp:6.3f}  {feat}")
        return "\n".join(lines)


def train(corpus_dir: str, language: str | None = None,
          n_estimators: int = 500, model_out: str | None = None,
          random_state: int = 0) -> TrainResult:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import accuracy_score, f1_score

    X, y, classes, _ = load_corpus(corpus_dir, language=language)
    if len(set(y)) < 2:
        raise ValueError("Il faut au moins 2 classes (ex. human/ et ai/).")

    clf = RandomForestClassifier(n_estimators=n_estimators,
                                 random_state=random_state, n_jobs=-1)

    # Validation croisée stratifiée 5 plis : chaque texte est testé une fois,
    # comme décrit dans le chapitre (Figure 6.1C).
    n_splits = min(5, np.min(np.bincount(_encode(y))))
    n_splits = max(2, n_splits)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    accs, f1s, perclass = [], [], {c: [] for c in classes}
    for tr_idx, te_idx in skf.split(X, y):
        clf.fit(X[tr_idx], y[tr_idx])
        pred = clf.predict(X[te_idx])
        accs.append(accuracy_score(y[te_idx], pred) * 100)
        f1s.append(f1_score(y[te_idx], pred, average="macro", zero_division=0) * 100)
        for c in classes:
            perclass[c].append(
                f1_score(y[te_idx] == c, pred == c, zero_division=0) * 100)

    # Modèle final entraîné sur tout le corpus, pour les prédictions futures
    # et l'importance de Gini agrégée.
    clf.fit(X, y)
    importances = sorted(zip(FEATURE_NAMES, clf.feature_importances_),
                         key=lambda t: -t[1])

    if model_out:
        import joblib
        joblib.dump({"clf": clf, "classes": classes,
                     "features": FEATURE_NAMES, "language": language}, model_out)

    return TrainResult(
        classes=classes, n_samples=len(y),
        accuracy_mean=float(np.mean(accs)), accuracy_sd=float(np.std(accs)),
        f1_macro_mean=float(np.mean(f1s)), f1_macro_sd=float(np.std(f1s)),
        gini_importance=[(f, float(i)) for f, i in importances],
        per_class_f1={c: float(np.mean(v)) for c, v in perclass.items()},
    )


def _encode(y):
    classes = sorted(set(y))
    idx = {c: i for i, c in enumerate(classes)}
    return np.asarray([idx[v] for v in y])


def predict(model_path: str, text: str):
    import joblib
    bundle = joblib.load(model_path)
    clf, classes = bundle["clf"], bundle["classes"]
    fr = extract_features(text, language=bundle.get("language"))
    x = np.asarray([[fr.features.get(n, 0.0) for n in bundle["features"]]])
    proba = clf.predict_proba(x)[0]
    pred = clf.classes_[int(np.argmax(proba))]
    return {"prediction": str(pred),
            "probabilities": {str(c): float(p) for c, p in zip(clf.classes_, proba)}}


def pca_projection(X, n_components: int = 2):
    """PCA pour visualisation (case studies 3-4 du chapitre).

    Renvoie (coords, variance_expliquée, loadings)."""
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    Xs = StandardScaler().fit_transform(X)
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(Xs)
    return coords, pca.explained_variance_ratio_, pca.components_
