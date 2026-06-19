"""Service 5 (bonus) — fonctions C appelees depuis Python via ctypes.

Flask expose en REST des fonctions de calcul statistique implementees en
C (src/stats.c, compilees dans lib/) et appelees via le module c_bridge.
Interet : le C est beaucoup plus rapide que Python pur pour les calculs
intensifs (c'est ainsi que NumPy/SciPy sont construits en interne).
"""

import os
from flask import Flask, request, jsonify, send_from_directory

# c_bridge = le "pont" qui appelle les fonctions C. On l'alias en C pour ecrire
# C.moyenne(...), C.mediane(...), etc.
import c_bridge as C

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def validate_list(data, key, min_len=1):
    """Valide qu'une cle JSON contient une liste de nombres."""
    if data is None:
        raise ValueError("Corps de requete JSON manquant")
    if key not in data:
        raise ValueError(f"Cle '{key}' manquante dans la requete")
    values = data[key]
    if not isinstance(values, list) or len(values) < min_len:
        raise ValueError(f"'{key}' doit etre une liste d'au moins {min_len} valeur(s)")
    return [float(v) for v in values]   # force des floats (le C attend des double)


# Chaque route recoit du JSON, valide, puis DELEGUE le calcul a la fonction C
# correspondante (via c_bridge). Le champ 'moteur' rappelle que le calcul vient du C.
@app.route('/c/stats/describe', methods=['POST'])
def c_describe():
    data = request.get_json(silent=True)
    try:
        values = validate_list(data, 'data', min_len=2)
        result = {
            'n': len(values),
            'moyenne': C.moyenne(values),       # appel de la fonction C calcul_moyenne
            'mediane': C.mediane(values),
            'ecart_type': C.ecart_type(values),
            'variance': C.variance(values),
            'minimum': C.minimum(values),
            'maximum': C.maximum(values),
        }
        return jsonify({'moteur': 'C/ctypes', 'operation': 'description', 'resultat': result})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/c/stats/mean', methods=['POST'])
def c_mean():
    """Moyenne seule (fonction C calcul_moyenne)."""
    data = request.get_json(silent=True)
    try:
        values = validate_list(data, 'data')
        return jsonify({'moteur': 'C/ctypes', 'operation': 'moyenne', 'resultat': C.moyenne(values)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/c/stats/stddev', methods=['POST'])
def c_stddev():
    """Ecart-type (fonction C calcul_ecart_type)."""
    data = request.get_json(silent=True)
    try:
        values = validate_list(data, 'data', min_len=2)
        return jsonify({'moteur': 'C/ctypes', 'operation': 'ecart_type', 'resultat': C.ecart_type(values)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/c/stats/median', methods=['POST'])
def c_median():
    """Mediane (fonction C calcul_mediane, qui trie les valeurs)."""
    data = request.get_json(silent=True)
    try:
        values = validate_list(data, 'data')
        return jsonify({'moteur': 'C/ctypes', 'operation': 'mediane', 'resultat': C.mediane(values)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/c/stats/dot', methods=['POST'])
def c_dot():
    """Produit scalaire de deux vecteurs v1 et v2 (fonction C produit_scalaire)."""
    data = request.get_json(silent=True)
    try:
        v1 = validate_list(data, 'v1')
        v2 = validate_list(data, 'v2')
        if len(v1) != len(v2):              # produit scalaire = meme longueur obligatoire
            return jsonify({'erreur': 'v1 et v2 doivent avoir la meme longueur'}), 400
        return jsonify({'moteur': 'C/ctypes', 'operation': 'produit_scalaire', 'resultat': C.dot_product(v1, v2)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Route de "sante" : permet de verifier rapidement que le service tourne et de
# lister les routes disponibles (utile pour tester / documenter).
@app.route('/c/health', methods=['GET'])
def health():
    return jsonify({
        'statut': 'ok',
        'service': 'Service 5 - C/Python Bridge',
        'port': 5005,
        'routes': ['POST /c/stats/describe', 'POST /c/stats/mean',
                   'POST /c/stats/stddev', 'POST /c/stats/median', 'POST /c/stats/dot'],
        'client_test': 'GET /client',
    })


@app.route('/', methods=['GET'])
@app.route('/client', methods=['GET'])
def client():
    """Sert le client de test HTML (meme origine -> pas de souci CORS)."""
    return send_from_directory(BASE_DIR, 'test_client.html')


if __name__ == '__main__':
    app.run(debug=True, port=5005)   # serveur de dev sur le port 5005
