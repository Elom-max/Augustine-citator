"""Interface en ligne de commande StyloScan.

Sous-commandes :
  analyze  : score heuristique d'un texte (aucun entraînement requis)
  train    : entraîne un Random Forest sur un corpus étiqueté (+ CV, F1, Gini)
  predict  : prédit avec un modèle entraîné
  features : affiche le vecteur de features brut
"""

from __future__ import annotations

import argparse
import json
import sys


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def cmd_analyze(args):
    from . import analyze, report
    text = _read(args.input)
    fr, sc = analyze(text, language=args.lang)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(report.to_json(fr, sc))
    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(report.to_html(fr, sc, title=f"StyloScan — {args.input}"))
    # Résumé console
    print(f"Langue       : {fr.language}  ({fr.n_words} mots, {fr.n_sentences} phrases)")
    print(f"Indice d'IA  : {sc.score:.0f}/100  [{sc.band}] — {sc.band_label}")
    print(f"Fiabilité    : {sc.reliability}")
    print(f"Outil estimé : {sc.tool_guess}  (confiance : {sc.tool_confidence})")
    print("Par catégorie :")
    for c, v in sc.category_scores.items():
        print(f"   {v:5.1f}  {c}")
    if sc.pro_ai_evidence:
        print("Indices pro-IA :")
        for s, v, c in sc.pro_ai_evidence:
            print(f"   • {s} (valeur {v}, contribution {c})")
    if args.json:
        print(f"[écrit] {args.json}")
    if args.html:
        print(f"[écrit] {args.html}")


def cmd_features(args):
    from .features import extract_features, FEATURE_CATEGORIES
    fr = extract_features(_read(args.input), language=args.lang)
    if args.raw_json:
        print(json.dumps(fr.features, ensure_ascii=False, indent=2))
        return
    print(f"# langue={fr.language} mots={fr.n_words} phrases={fr.n_sentences}")
    for cat, names in FEATURE_CATEGORIES.items():
        print(f"\n[{cat}]")
        for n in names:
            print(f"  {n:24s} {fr.features.get(n, 0):.4f}")


def cmd_train(args):
    from .model import train
    res = train(args.corpus, language=args.lang,
                n_estimators=args.trees, model_out=args.out)
    print(res.summary())
    if args.out:
        print(f"\n[modèle écrit] {args.out}")
    if args.gini_plot:
        from .viz import plot_gini_importance
        plot_gini_importance(res.gini_importance, args.gini_plot)
        print(f"[figure écrite] {args.gini_plot}")


def cmd_predict(args):
    from .model import predict
    out = predict(args.model, _read(args.input))
    print(json.dumps(out, ensure_ascii=False, indent=2))


def build_parser():
    p = argparse.ArgumentParser(
        prog="styloscan",
        description="Stylométrie pour détecter/quantifier l'usage d'IA dans l'écrit scientifique (FR/EN/NL).")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="score heuristique d'un texte")
    a.add_argument("input", help="fichier texte (ou '-' pour stdin)")
    a.add_argument("--lang", choices=["fr", "en", "nl"], default=None,
                   help="forcer la langue (sinon détection auto)")
    a.add_argument("--json", help="écrire le rapport JSON ici")
    a.add_argument("--html", help="écrire le rapport HTML ici")
    a.set_defaults(func=cmd_analyze)

    fe = sub.add_parser("features", help="affiche le vecteur de features")
    fe.add_argument("input")
    fe.add_argument("--lang", choices=["fr", "en", "nl"], default=None)
    fe.add_argument("--raw-json", action="store_true")
    fe.set_defaults(func=cmd_features)

    t = sub.add_parser("train", help="entraîne un RF sur un corpus étiqueté")
    t.add_argument("corpus", help="dossier avec sous-dossiers de classes (human/, ai/)")
    t.add_argument("--lang", choices=["fr", "en", "nl"], default=None)
    t.add_argument("--trees", type=int, default=500)
    t.add_argument("--out", help="chemin de sauvegarde du modèle (.joblib)")
    t.add_argument("--gini-plot", help="chemin de la figure d'importance de Gini")
    t.set_defaults(func=cmd_train)

    pr = sub.add_parser("predict", help="prédit avec un modèle entraîné")
    pr.add_argument("input")
    pr.add_argument("--model", required=True)
    pr.set_defaults(func=cmd_predict)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
