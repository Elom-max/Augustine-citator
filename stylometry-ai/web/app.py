"""Mini-application web StyloScan : coller un texte → rapport stylométrique.

Lancement :
    cd stylometry-ai
    PYTHONPATH=. python3 web/app.py
    # puis ouvrir http://127.0.0.1:5000
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request

from styloscan import analyze
from styloscan import report as rpt

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result_html = None
    text = ""
    lang = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        lang = request.form.get("lang", "") or None
        if text.strip():
            fr, sc = analyze(text, language=lang)
            # On réutilise le rendu HTML du rapport (corps seulement).
            result_html = rpt.to_html(fr, sc, title="Résultat")
    return render_template("index.html", result_html=result_html,
                           text=text, lang=lang or "")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    lang = data.get("lang") or None
    if not text.strip():
        return {"error": "champ 'text' vide"}, 400
    fr, sc = analyze(text, language=lang)
    return rpt.to_dict(fr, sc)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
