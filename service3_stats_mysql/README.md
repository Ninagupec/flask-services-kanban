# Service 3 — Statistiques depuis MySQL

API REST Flask qui calcule des statistiques sur des séries **lues dans la base MySQL** `flask_stats` (table `donnees`, alimentée par le Service 4). Utilise mysql-connector-python, NumPy et SciPy.

## Initialisation de la base

```bash
mysql -u root < ../sql/init_db.sql        # crée la base flask_stats + la table donnees (+ données initiales)
```

## Installation

```bash
cd service3_stats_mysql
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# créer un fichier .env avec DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME
python app.py             # http://localhost:5003
```

> Coordination avec l'Étudiant D (Service 4) : même base `flask_stats`, même table `donnees`. Les identifiants sont lus depuis `.env` (jamais committé, voir `.gitignore`).

## Routes disponibles

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/db/stats/describe?serie=serie_A` | Stats descriptives d'une série lue depuis MySQL |
| GET | `/db/stats/correlation?serie_x=...&serie_y=...` | Corrélation de Pearson entre deux séries |
| GET | `/client` | Client de test HTML |

### GET /db/stats/describe
Paramètre `serie` (requis). Retourne `n`, `moyenne`, `mediane`, `ecart_type`, `minimum`, `maximum`.
- `400` si `serie` manquant · `404` si la série n'existe pas dans la base.

### GET /db/stats/correlation
Paramètres `serie_x` et `serie_y` (requis). Les longueurs sont alignées sur la plus courte.
- `400` si un paramètre manque ou si une série est constante (variance nulle).

## Exemples curl

```bash
curl "http://localhost:5003/db/stats/describe?serie=serie_A"
curl "http://localhost:5003/db/stats/correlation?serie_x=serie_A&serie_y=serie_B"
```

## Codes HTTP

| Code | Quand |
|------|-------|
| 200 | Succès |
| 400 | Paramètre manquant / série constante |
| 404 | Série inexistante dans la base |
| 500 | Erreur de connexion / requête MySQL |

## Tests de la partie client

- **test_client.py** : tests unitaires (`unittest`) — describe, série inexistante (404), paramètre manquant (400), corrélation.
- **test_client.html** : client web (`fetch`), servi via `GET /client`.
