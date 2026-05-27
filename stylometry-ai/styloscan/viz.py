"""Visualisations façon chapitre : importance de Gini, PCA, violin plots.

matplotlib en backend non-interactif (Agg) : fonctionne sans affichage.
Chaque fonction enregistre une figure et renvoie le chemin.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_gini_importance(importances, out_path: str, top: int = 15):
    items = importances[:top][::-1]
    labels = [f for f, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7, max(3, 0.35 * len(items))))
    ax.barh(labels, vals, color="#1565c0")
    ax.set_xlabel("Importance de Gini (mean decrease in impurity)")
    ax.set_title("Features les plus discriminantes (Random Forest)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    return out_path


def plot_pca(coords, labels, explained, out_path: str):
    fig, ax = plt.subplots(figsize=(6.5, 5))
    labels = np.asarray(labels)
    for cls in sorted(set(labels)):
        m = labels == cls
        ax.scatter(coords[m, 0], coords[m, 1], label=str(cls), alpha=0.75, s=28)
    ax.set_xlabel(f"PC1 ({explained[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({explained[1]*100:.1f}%)")
    ax.set_title("PCA des profils stylométriques")
    ax.legend()
    ax.axhline(0, color="#ccc", lw=0.6)
    ax.axvline(0, color="#ccc", lw=0.6)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    return out_path


def plot_violin(values_by_class: dict, feature_name: str, out_path: str):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    classes = list(values_by_class.keys())
    data = [values_by_class[c] for c in classes]
    parts = ax.violinplot(data, showmedians=True)
    ax.set_xticks(range(1, len(classes) + 1))
    ax.set_xticklabels(classes)
    ax.set_ylabel(feature_name)
    ax.set_title(f"Distribution de « {feature_name} » par classe")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    return out_path
