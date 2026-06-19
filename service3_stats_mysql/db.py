"""Module de connexion MySQL pour le Service 3.

Lit les identifiants depuis les variables d'environnement (.env) et
fournit l'acces aux series de la table `donnees`.
"""

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Retourne une connexion MySQL a partir des variables d'environnement."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'flask_stats'),
    )


def fetch_series(nom_serie):
    """Recupere toutes les valeurs d'une serie depuis la table donnees."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT valeur FROM donnees WHERE nom_serie = %s ORDER BY date_mesure',
        (nom_serie,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        raise ValueError(f"Aucune donnee trouvee pour la serie '{nom_serie}'")
    return [float(row[0]) for row in rows]
