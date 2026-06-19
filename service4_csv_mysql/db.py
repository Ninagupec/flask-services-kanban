"""Acces base de donnees pour les services 3 et 4 — SQLite (defaut) OU MySQL.

Le moteur est choisi par la variable d'environnement DB_ENGINE :
  - 'sqlite' (defaut) : base fichier locale ../data/flask_stats.db. ZERO
    installation : la base et un jeu de donnees d'exemple sont crees
    automatiquement la premiere fois. Marche partout avec juste Python.
  - 'mysql' : serveur MySQL (identifiants lus dans .env). Pour la demo
    conforme au sujet du TP.

Les services 3 et 4 partagent la meme base.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').strip().lower()
# Placeholder des requetes parametrees : '?' en SQLite, '%s' en MySQL.
PLACEHOLDER = '%s' if DB_ENGINE == 'mysql' else '?'

# Base SQLite partagee par les services 3 et 4 : <repo>/data/flask_stats.db
_SQLITE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'flask_stats.db'))

# Jeu de donnees d'exemple (seed initial en SQLite si la table est vide).
_SEED = [
    ('serie_A', 12.50, 'temperature', '2024-01-15'),
    ('serie_A', 15.30, 'temperature', '2024-01-16'),
    ('serie_A', 8.70, 'temperature', '2024-01-17'),
    ('serie_A', 21.00, 'temperature', '2024-01-18'),
    ('serie_A', 13.20, 'temperature', '2024-01-19'),
    ('serie_B', 45.10, 'pression', '2024-01-15'),
    ('serie_B', 52.80, 'pression', '2024-01-16'),
    ('serie_B', 48.60, 'pression', '2024-01-17'),
    ('serie_B', 55.20, 'pression', '2024-01-18'),
]


def _init_sqlite():
    """Cree la base SQLite + la table + le seed si besoin (idempotent)."""
    import sqlite3
    os.makedirs(os.path.dirname(_SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(_SQLITE_PATH)
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS donnees ('
        ' id INTEGER PRIMARY KEY AUTOINCREMENT,'
        ' nom_serie TEXT NOT NULL,'
        ' valeur REAL NOT NULL,'
        ' categorie TEXT,'
        ' date_mesure TEXT,'
        ' created_at TEXT DEFAULT CURRENT_TIMESTAMP)'
    )
    cur.execute('SELECT COUNT(*) FROM donnees')
    if cur.fetchone()[0] == 0:
        cur.executemany(
            'INSERT INTO donnees (nom_serie, valeur, categorie, date_mesure)'
            ' VALUES (?, ?, ?, ?)', _SEED)
    conn.commit()
    conn.close()


if DB_ENGINE != 'mysql':
    _init_sqlite()


def get_connection():
    """Retourne une connexion vers le moteur actif (SQLite ou MySQL)."""
    if DB_ENGINE == 'mysql':
        import mysql.connector
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'flask_stats'),
        )
    import sqlite3
    return sqlite3.connect(_SQLITE_PATH)


def fetch_series(nom_serie):
    """Recupere toutes les valeurs d'une serie depuis la table donnees."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT valeur FROM donnees WHERE nom_serie = ' + PLACEHOLDER
        + ' ORDER BY date_mesure', (nom_serie,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        raise ValueError(f"Aucune donnee trouvee pour la serie '{nom_serie}'")
    return [float(row[0]) for row in rows]
