"""Module de connexion MySQL pour le Service 3.

Lit les identifiants depuis les variables d'environnement (.env) et
fournit l'acces aux series de la table `donnees`.
"""

import os

import mysql.connector             # connecteur officiel Python <-> MySQL
from dotenv import load_dotenv     # charge le fichier .env dans les variables d'env

# Lit le fichier .env (DB_HOST, DB_USER, ...) et le rend accessible via os.getenv.
# On NE met JAMAIS les identifiants en dur dans le code (securite) : .env est
# ignore par Git.
load_dotenv()


def get_connection():
    """Retourne une connexion MySQL a partir des variables d'environnement."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),     # adresse du serveur MySQL
        port=int(os.getenv('DB_PORT', 3306)),       # port (3306 par defaut)
        user=os.getenv('DB_USER'),                  # utilisateur applicatif
        password=os.getenv('DB_PASSWORD'),          # mot de passe
        database=os.getenv('DB_NAME', 'flask_stats'),  # base a utiliser
    )


def fetch_series(nom_serie):
    """Recupere toutes les valeurs d'une serie depuis la table donnees."""
    conn = get_connection()
    cursor = conn.cursor()         # le curseur execute les requetes SQL
    # Requete PARAMETREE : le %s est remplace de facon securisee par nom_serie.
    # Cela evite les injections SQL (on ne concatene jamais directement).
    cursor.execute(
        'SELECT valeur FROM donnees WHERE nom_serie = %s ORDER BY date_mesure',
        (nom_serie,),
    )
    rows = cursor.fetchall()       # recupere toutes les lignes resultat
    cursor.close()
    conn.close()                   # toujours fermer curseur et connexion
    if not rows:                   # aucune ligne -> la serie n'existe pas
        raise ValueError(f"Aucune donnee trouvee pour la serie '{nom_serie}'")
    # rows est une liste de tuples [(12.5,), (15.3,), ...] -> on extrait les floats.
    return [float(row[0]) for row in rows]
