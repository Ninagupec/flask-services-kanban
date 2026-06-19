"""Service 1 — Calculs matriciels (Etudiant A).

API REST Flask exposant cinq operations sur des matrices envoyees en
JSON : addition, multiplication, transposee, determinant, inverse.
S'appuie sur NumPy via le module matrices.py.
"""

import os
from flask import Flask, request, jsonify, send_from_directory

import matrices

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/matrices/add', methods=['POST'])
def add_matrices():
    """Additionne deux matrices A et B de memes dimensions."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        b = matrices.parse_matrix(data, 'B')
        return jsonify({'operation': 'addition', 'resultat': matrices.addition(a, b)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/multiply', methods=['POST'])
def multiply_matrices():
    """Produit matriciel A x B."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        b = matrices.parse_matrix(data, 'B')
        return jsonify({'operation': 'multiplication', 'resultat': matrices.multiplication(a, b)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/transpose', methods=['POST'])
def transpose_matrix():
    """Transposee de la matrice A."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        return jsonify({'operation': 'transposee', 'resultat': matrices.transposee(a)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/determinant', methods=['POST'])
def determinant_matrix():
    """Determinant d'une matrice carree A."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        return jsonify({'operation': 'determinant', 'resultat': matrices.determinant(a)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/matrices/inverse', methods=['POST'])
def inverse_matrix():
    """Inverse d'une matrice carree non singuliere A."""
    data = request.get_json(silent=True)
    try:
        a = matrices.parse_matrix(data, 'A')
        return jsonify({'operation': 'inverse', 'resultat': matrices.inverse(a)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


@app.route('/', methods=['GET'])
@app.route('/client', methods=['GET'])
def client():
    """Sert le client de test HTML (meme origine -> pas de souci CORS)."""
    return send_from_directory(BASE_DIR, 'test_client.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
