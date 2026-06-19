"""Service 1 — Calculs matriciels (Etudiant A).

API REST Flask exposant cinq operations sur des matrices envoyees en
JSON : addition, multiplication, transposee, determinant, inverse.
S'appuie sur NumPy via le module matrices.py.
"""

import os
# Flask : micro-framework web. request = la requete recue, jsonify = fabrique
# une reponse JSON, send_from_directory = renvoie un fichier (la page de test).
from flask import Flask, request, jsonify, send_from_directory

# Module local : toute la logique de calcul matriciel est isolee dans matrices.py
# (bonne pratique : separer les routes web et les calculs).
import matrices

app = Flask(__name__)              # cree l'application web
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier de ce fichier


# @app.route : associe une URL + une methode HTTP a une fonction Python.
# Toutes les routes de calcul sont en POST car le client envoie des donnees (JSON).
@app.route('/matrices/add', methods=['POST'])
def add_matrices():
    """Additionne deux matrices A et B de memes dimensions."""
    data = request.get_json(silent=True)   # lit le corps JSON (None si invalide)
    try:
        # parse_matrix verifie et convertit la liste de listes en tableau NumPy.
        a = matrices.parse_matrix(data, 'A')
        b = matrices.parse_matrix(data, 'B')
        # On renvoie l'operation et le resultat au format JSON (HTTP 200 par defaut).
        return jsonify({'operation': 'addition', 'resultat': matrices.addition(a, b)})
    except (ValueError, TypeError) as e:
        # Entree invalide (mauvaises dimensions, valeur non numerique...) -> HTTP 400.
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/multiply', methods=['POST'])
def multiply_matrices():
    """Produit matriciel A x B."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        b = matrices.parse_matrix(data, 'B')
        # multiplication verifie que colonnes(A) == lignes(B) avant de calculer.
        return jsonify({'operation': 'multiplication', 'resultat': matrices.multiplication(a, b)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/transpose', methods=['POST'])
def transpose_matrix():
    """Transposee de la matrice A (les lignes deviennent les colonnes)."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        return jsonify({'operation': 'transposee', 'resultat': matrices.transposee(a)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/determinant', methods=['POST'])
def determinant_matrix():
    """Determinant d'une matrice carree A (un seul nombre)."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        # determinant verifie d'abord que la matrice est carree (sinon 400).
        return jsonify({'operation': 'determinant', 'resultat': matrices.determinant(a)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/inverse', methods=['POST'])
def inverse_matrix():
    """Inverse d'une matrice carree non singuliere A."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        # inverse verifie carree ET determinant != 0 (une matrice singuliere
        # n'a pas d'inverse) -> sinon 400.
        return jsonify({'operation': 'inverse', 'resultat': matrices.inverse(a)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Page de test HTML servie sur '/' ET '/client'. Comme elle est servie par le
# service lui-meme, les appels fetch du navigateur sont en "meme origine" -> pas
# de blocage CORS.
@app.route('/', methods=['GET'])
@app.route('/client', methods=['GET'])
def client():
    """Sert le client de test HTML (meme origine -> pas de souci CORS)."""
    return send_from_directory(BASE_DIR, 'test_client.html')


# Point d'entree : on lance le serveur de developpement Flask sur le port 5001.
# debug=True recharge le code automatiquement et affiche les erreurs detaillees.
if __name__ == '__main__':
    app.run(debug=True, port=5001)
