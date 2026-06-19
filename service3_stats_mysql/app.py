"""Service 3 — Statistiques depuis MySQL (Etudiant C).

Memes calculs que le Service 2, mais les donnees sont lues dans la table
MySQL `donnees` (alimentee par le Service 4) au lieu d'etre recues en
JSON. Utilise Flask, mysql-connector-python, NumPy et SciPy.
"""

import os

import numpy as np
from scipy import stats
from flask import Flask, request, jsonify, send_from_directory

from db import fetch_series, DB_ENGINE

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/db/stats/describe', methods=['GET'])
def db_describe():
    """Statistiques descriptives d'une serie lue depuis MySQL."""
    nom_serie = request.args.get('serie')
    if not nom_serie:
        return jsonify({'erreur': "Parametre 'serie' manquant"}), 400
    try:
        values = np.array(fetch_series(nom_serie))
        result = {
            'serie': nom_serie,
            'n': int(len(values)),
            'moyenne': round(float(np.mean(values)), 4),
            'mediane': round(float(np.median(values)), 4),
            'ecart_type': round(float(np.std(values, ddof=1)), 4),
            'minimum': round(float(np.min(values)), 4),
            'maximum': round(float(np.max(values)), 4),
        }
        return jsonify({'source': DB_ENGINE, 'resultat': result})
    except ValueError as e:
        return jsonify({'erreur': str(e)}), 404
    except Exception as e:
        return jsonify({'erreur': 'Erreur base de donnees', 'detail': str(e)}), 500


@app.route('/db/stats/correlation', methods=['GET'])
def db_correlation():
    """Correlation de Pearson entre deux series lues depuis MySQL."""
    serie_x = request.args.get('serie_x')
    serie_y = request.args.get('serie_y')
    if not serie_x or not serie_y:
        return jsonify({'erreur': 'Parametres serie_x et serie_y requis'}), 400
    try:
        x = np.array(fetch_series(serie_x))
        y = np.array(fetch_series(serie_y))
        n = min(len(x), len(y))
        x, y = x[:n], y[:n]  # aligner les longueurs
        if np.std(x) == 0 or np.std(y) == 0:
            return jsonify({'erreur': 'correlation indefinie : variance nulle (serie constante)'}), 400
        r, p_value = stats.pearsonr(x, y)
        return jsonify({
            'source': DB_ENGINE,
            'series': {'x': serie_x, 'y': serie_y, 'n_points': n},
            'resultat': {
                'r': round(float(r), 4),
                'p_value': round(float(p_value), 6),
                'significatif': bool(p_value < 0.05),
            },
        })
    except ValueError as e:
        return jsonify({'erreur': str(e)}), 404
    except Exception as e:
        return jsonify({'erreur': 'Erreur base de donnees', 'detail': str(e)}), 500


@app.route('/', methods=['GET'])
@app.route('/client', methods=['GET'])
def client():
    """Sert le client de test HTML (meme origine -> pas de souci CORS)."""
    return send_from_directory(BASE_DIR, 'test_client.html')


if __name__ == '__main__':
    app.run(debug=True, port=5003)
