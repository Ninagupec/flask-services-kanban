# Service 4 — Chargement CSV vers MySQL

API REST Flask qui charge un fichier CSV dans la table MySQL `donnees`. Fournit les données lues ensuite par le Service 3. Utilise pandas et mysql-connector-python.

## Installation

```bash
cd service4_csv_mysql
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# créer un fichier .env avec DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME
python app.py             # http://localhost:5004
```

> La base et la table sont créées par `sql/init_db.sql` (voir Service 3). Coordination avec l'Étudiant C : même base `flask_stats`, même table `donnees`.

## Configuration (.env)

Les identifiants MySQL sont lus depuis `.env` (jamais committé, voir `.gitignore`) :
`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

## Routes disponibles

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/upload/csv` | Charge un CSV (multipart, champ `file`) dans la table `donnees` |
| GET | `/upload/series` | Liste les séries chargées (nb de points, dates min/max) |
| GET | `/client` | Client de test HTML |

### POST /upload/csv
- Champ multipart `file` (extension `.csv`, max 5 Mo).
- Colonnes obligatoires : `nom_serie`, `valeur`. Optionnelles : `categorie`, `date_mesure`.
- Les valeurs non numériques de `valeur` sont ignorées (comptées dans `lignes_invalides_ignorees`).

Réponse 201 :
```json
{"statut": "success", "lignes_inserees": 30, "lignes_invalides_ignorees": 0,
 "message": "30 ligne(s) chargee(s) dans la table donnees"}
```

## Exemples curl

```bash
curl -X POST http://localhost:5004/upload/csv -F 'file=@../data/donnees_exemple.csv'
curl http://localhost:5004/upload/series
```

## Validation effectuée

1. Présence du champ `file` et nom non vide.
2. Extension `.csv` uniquement.
3. Taille ≤ 5 Mo (sinon 413).
4. CSV lisible par pandas (sinon 400).
5. Colonnes obligatoires présentes (sinon 400).
6. Conversion numérique de `valeur` ; lignes non numériques ignorées.

## Codes HTTP

| Code | Quand |
|------|-------|
| 201 | Insertion réussie |
| 400 | Fichier manquant, mauvaise extension, colonnes manquantes, CSV illisible |
| 413 | Fichier trop volumineux (> 5 Mo) |
| 500 | Erreur de connexion / requête MySQL |

## Tests de la partie client

- **test_client.py** : tests unitaires (`unittest`) — upload valide, colonne manquante, mauvaise extension, fichier manquant, valeurs non numériques ignorées, liste des séries.
- **test_client.html** : page web pour téléverser un CSV et lister les séries (servie via `GET /client`).
