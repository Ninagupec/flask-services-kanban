"""Service 4 — Chargement d'un CSV vers MySQL (Etudiant D).

API REST Flask qui charge les donnees d'un fichier CSV dans la table
MySQL `donnees`. C'est le fournisseur de donnees du Service 3.
Utilise pandas et mysql-connector-python. Partage la base flask_stats.
"""

import io
import os

import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory

# Charge les variables définies dans .env
load_dotenv()
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLONNES_REQUISES = {'nom_serie', 'valeur'}
COLONNES_VALIDES = {'nom_serie', 'valeur', 'categorie', 'date_mesure'}
TAILLE_MAX_OCTETS = 5 * 1024 * 1024  # 5 Mo

def get_connection():
    """Connexion MySQL a partir des variables d'environnement (.env)."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'flask_stats'),
    )

@app.route('/upload/csv', methods=['POST'])
def upload_csv():
    """Charge un CSV (champ multipart 'file') dans la table donnees."""
    # 1. Presence du fichier
    if 'file' not in request.files:
        return jsonify({'erreur': 'Aucun fichier envoye (cle "file" manquante)'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'erreur': 'Nom de fichier vide'}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({'erreur': 'Seuls les fichiers .csv sont acceptes'}), 400

    # 2. Lecture et validation du contenu
    try:
        content = file.read()
        if len(content) > TAILLE_MAX_OCTETS:
            return jsonify({'erreur': 'Fichier trop volumineux (max 5 Mo)'}), 413
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        return jsonify({'erreur': f'Lecture CSV impossible : {e}'}), 400

    # 3. Colonnes obligatoires
    # set(df.columns) : Ensemble des noms de colonnes du CSV.
    # COLONNES_REQUISES - set(df.columns) : Calcul des colonnes obligatoires qui ne sont pas présentes.
    colonnes_manquantes = COLONNES_REQUISES - set(df.columns)
    if colonnes_manquantes:
        return jsonify({
            'erreur': 'Colonnes obligatoires manquantes',
            'manquantes': sorted(colonnes_manquantes),
        }), 400

    # 4. Nettoyage : ne garder que les colonnes valides, valeurs numeriques
    df = df[[c for c in df.columns if c in COLONNES_VALIDES]]
    # pd.to_numeric : Convertit la colonne valeur en nombres.
    # errors='coerce' : Si une valeur n’est pas convertible, elle devient NaN (valeur manquante).
    df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
    # lignes_invalides : Nombre de lignes qui seront ignorées.
    lignes_invalides = int(df['valeur'].isna().sum())
    # dropna(subset=['valeur']) : Supprime les lignes où valeur est NaN.
    df = df.dropna(subset=['valeur'])
    if df.empty:
        return jsonify({'erreur': 'Aucune ligne valide dans le CSV'}), 400

    # Booléen indiquant si la colonne categorie existe.
    a_categorie = 'categorie' in df.columns
    # Booléen indiquant si la colonne date_mesure existe.
    a_date = 'date_mesure' in df.columns

    # 5. Insertion MySQL
    try:
        # Ouvre une connexion à la base MySQL.
        conn = get_connection()
        # Crée un curseur pour exécuter des requêtes SQL.
        cursor = conn.cursor()
        # Compteur de lignes insérées.
        insertions = 0
        # Parcourt chaque ligne du DataFrame.
        for _, row in df.iterrows():
            # Exécute une requête INSERT
            cursor.execute(
                'INSERT INTO donnees (nom_serie, valeur, categorie, date_mesure)'
                ' VALUES (%s, %s, %s, %s)',
                (
                    str(row['nom_serie']),
                    float(row['valeur']),
                    str(row['categorie']) if a_categorie else None,
                    str(row['date_mesure']) if a_date else None,
                ),
            )
            insertions += 1
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'erreur': 'Erreur base de donnees', 'detail': str(e)}), 500

    return jsonify({
        'statut': 'success',
        'lignes_inserees': insertions,
        'lignes_invalides_ignorees': lignes_invalides,
        'message': f'{insertions} ligne(s) chargee(s) dans la table donnees',
    # Code HTTP 201 : Création réussie.
    }), 201


@app.route('/upload/series', methods=['GET'])
def list_series():
    """Liste les series chargees et leur nombre de points."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT nom_serie, COUNT(*) AS n, MIN(date_mesure), MAX(date_mesure)'
            ' FROM donnees GROUP BY nom_serie ORDER BY nom_serie'
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Transforme chaque ligne SQL (r) en dict
        series = [
            {'serie': r[0], 'n_points': r[1], 'debut': str(r[2]), 'fin': str(r[3])}
            for r in rows
        ]
        return jsonify({'series': series, 'total': len(series)})
    except Exception as e:
        return jsonify({'erreur': 'Erreur base de donnees', 'detail': str(e)}), 500

@app.route('/client', methods=['GET'])
def client():
    """Sert le client de test HTML (meme origine -> pas de souci CORS)."""
    return send_from_directory(BASE_DIR, 'test_client.html')

if __name__ == '__main__':
    app.run(debug=True, port=5004)