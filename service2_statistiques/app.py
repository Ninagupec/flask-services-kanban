"""Service 2 — Fonctions statistiques sur des donnees JSON (Etudiant B).

API REST Flask qui calcule des statistiques sur des series de nombres
envoyees en JSON. Utilise NumPy et SciPy.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
import numpy as np            # calculs de base (moyenne, ecart-type, quartiles...)
from scipy import stats       # tests statistiques (Pearson, Shapiro, Student)

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def validate_data(data, key='data'):
    """Valide et retourne une liste de nombres en tableau NumPy.

    Verifie que le JSON existe, que la cle est presente et qu'on a bien une
    liste d'au moins 2 valeurs (en dessous, les statistiques n'ont pas de sens).
    """
    if data is None:
        raise ValueError("Corps de requete JSON manquant")
    if key not in data:
        raise ValueError(f"Cle '{key}' manquante dans la requete")
    values = data[key]
    if not isinstance(values, list) or len(values) < 2:
        raise ValueError("'%s' doit etre une liste d'au moins 2 valeurs" % key)
    return np.array(values, dtype=float)   # tableau NumPy pret pour les calculs


@app.route('/stats/describe', methods=['POST'])
def describe():
    """Statistiques descriptives d'un tableau de valeurs."""
    data = request.get_json(silent=True)
    try:
        values = validate_data(data)
        result = {
            'n':          int(len(values)),                          # nb de valeurs
            'moyenne':    round(float(np.mean(values)), 4),          # moyenne
            'mediane':    round(float(np.median(values)), 4),        # valeur centrale
            # ddof=1 : ecart-type/variance NON biaises (division par n-1), car on
            # travaille sur un echantillon et non sur la population entiere.
            'ecart_type': round(float(np.std(values, ddof=1)), 4),
            'variance':   round(float(np.var(values, ddof=1)), 4),
            'minimum':    round(float(np.min(values)), 4),
            'maximum':    round(float(np.max(values)), 4),
            'q1':         round(float(np.percentile(values, 25)), 4),  # 1er quartile
            'q3':         round(float(np.percentile(values, 75)), 4),  # 3e quartile
            'etendue':    round(float(np.ptp(values)), 4),             # max - min
        }
        return jsonify({'operation': 'description', 'resultat': result})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400   # entree invalide -> 400


@app.route('/stats/correlation', methods=['POST'])
def correlation():
    """Coefficient de correlation de Pearson entre deux series x et y."""
    data = request.get_json(silent=True)
    try:
        x = validate_data(data, 'x')
        y = validate_data(data, 'y')
        if len(x) != len(y):                  # Pearson exige deux series de meme taille
            return jsonify({'erreur': 'x et y doivent avoir la meme longueur'}), 400
        # Fix #20 : si une serie est constante (variance nulle), la correlation
        # de Pearson est indefinie (division par zero -> NaN). NaN n'est pas du
        # JSON valide, on renvoie donc une erreur 400 explicite.
        if np.std(x) == 0 or np.std(y) == 0:
            return jsonify({'erreur': 'correlation indefinie : variance nulle (serie constante)'}), 400
        # r dans [-1, 1] : +1 = lien positif parfait, -1 = negatif, 0 = aucun.
        # p_value : probabilite que le lien soit du au hasard.
        r, p_value = stats.pearsonr(x, y)
        interpretation = (                    # etiquette lisible selon la force du lien
            'forte' if abs(r) > 0.7
            else 'moderee' if abs(r) > 0.4
            else 'faible'
        )
        return jsonify({
            'operation': 'correlation_pearson',
            'resultat': {
                'r': round(float(r), 4),
                'p_value': round(float(p_value), 6),
                'interpretation': interpretation,
                'significatif': bool(p_value < 0.05),  # significatif si p < 5%
            },
        })
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/stats/test_normalite', methods=['POST'])
def test_normalite():
    """Test de Shapiro-Wilk : la serie suit-elle une loi normale ?"""
    data = request.get_json(silent=True)
    try:
        values = validate_data(data)
        if len(values) > 5000:               # Shapiro-Wilk n'est fiable que <= 5000 valeurs
            return jsonify({'erreur': 'Shapiro-Wilk limite a 5000 valeurs'}), 400
        stat, p_value = stats.shapiro(values)
        return jsonify({
            'operation': 'test_normalite_shapiro_wilk',
            'resultat': {
                'statistique': round(float(stat), 6),
                'p_value': round(float(p_value), 6),
                # Convention : p > 0.05 -> on ne rejette pas la normalite.
                'est_normale': bool(p_value > 0.05),
                'interpretation': (
                    'Distribution normale (p > 0.05)' if p_value > 0.05
                    else 'Distribution non normale (p <= 0.05)'
                ),
            },
        })
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/stats/test_student', methods=['POST'])
def test_student():
    """Test t de Student : compare les moyennes de deux groupes independants."""
    data = request.get_json(silent=True)
    try:
        groupe1 = validate_data(data, 'groupe1')
        groupe2 = validate_data(data, 'groupe2')
        # ttest_ind : repond a "les deux groupes ont-ils des moyennes vraiment
        # differentes, ou est-ce du hasard ?"
        t_stat, p_value = stats.ttest_ind(groupe1, groupe2)
        return jsonify({
            'operation': 'test_t_student',
            'resultat': {
                't_statistique': round(float(t_stat), 4),
                'p_value': round(float(p_value), 6),
                'difference_significative': bool(p_value < 0.05),  # difference reelle si p < 5%
            },
        })
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Page de test HTML (meme origine -> pas de souci CORS).
@app.route('/', methods=['GET'])
@app.route('/client', methods=['GET'])
def client():
    """Sert le client de test HTML (meme origine -> pas de souci CORS)."""
    return send_from_directory(BASE_DIR, 'test_client.html')


if __name__ == '__main__':
    app.run(debug=True, port=5002)   # serveur de dev sur le port 5002
