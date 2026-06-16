# flask-services-kanban

Projet du TP2 R2.10 (GPO) — un ensemble de **microservices web Python Flask**, gérés via un tableau Kanban GitHub Projects et un workflow Git par branches / pull requests / code review.

## Équipe et répartition

| Étudiant | Membre | Service(s) |
|----------|--------|------------|
| A & C | Nina Gimenez | Service 1 (matrices) & Service 3 (stats MySQL) |
| B | Thomas De Sousa | Service 2 (statistiques JSON) |
| D | Aaron Piscitello | Service 4 (chargement CSV → MySQL) |
| Bonus (binôme) | Thomas & Aaron | Service 5 (fonctions C via ctypes) |

## Architecture

Quatre microservices REST indépendants (+ un service bonus). Les services 3 et 4 partagent la même base MySQL `flask_stats` (table `donnees`).

| Service | Dossier | Port | Description |
|---------|---------|------|-------------|
| 1 | `service1_matrices/` | 5001 | Calculs matriciels (NumPy) |
| 2 | `service2_statistiques/` | 5002 | Statistiques sur données JSON (NumPy/SciPy) |
| 3 | `service3_stats_mysql/` | 5003 | Statistiques lues depuis MySQL |
| 4 | `service4_csv_mysql/` | 5004 | Chargement d'un CSV vers MySQL (pandas) |
| 5 (bonus) | `service5_c_python/` | 5005 | Fonctions de calcul en C appelées via ctypes |

```
flask-services-kanban/
├── service1_matrices/        # Service 1 (Étudiant A)
├── service2_statistiques/    # Service 2 (Étudiant B)
├── service3_stats_mysql/     # Service 3 (Étudiant C)
├── service4_csv_mysql/       # Service 4 (Étudiant D)
├── service5_c_python/        # Service 5 (bonus)
├── data/donnees_exemple.csv  # Jeu de démonstration (Services 3 & 4)
├── sql/init_db.sql           # Création base + table MySQL
└── README.md
```

## Démarrer un service

```bash
cd serviceX_xxx
python -m venv venv && source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Chaque service expose `GET /` (liste des routes) et `GET /client` (client de test HTML). Voir le `README.md` de chaque service pour le détail des routes et des exemples `curl`.

## Base de données MySQL (Services 3 & 4)

```bash
mysql -u root < sql/init_db.sql          # crée la base flask_stats + la table donnees
```

Les identifiants sont lus depuis un fichier `.env` (jamais committé — voir `.gitignore`) ; un modèle est fourni dans chaque service concerné (`.env.example`).

## Tests de la partie client

Chaque service fournit, après les tests `curl`/Postman :
- un **client Python** `test_client.py` (tests unitaires `unittest`) ;
- un **client web** `test_client.html` (formulaires `fetch` JSON), servi via `GET /client`.

## Workflow Git du groupe

- `main` : code testé et validé uniquement.
- `feature/sX-...` : développement d'une fonctionnalité ; `fix/sX-...` : correction de bug.
- Une **pull request** par fonctionnalité, **revue par un autre membre** avant le merge, fermeture des issues via `Closes #N`.
- Commits conventionnels : `feat(s1): ...`, `fix(s2): ...`, `test(s4): ...`, `docs(s1): ...`.

## Codes HTTP

`200` succès · `201` création (insertion) · `400` requête invalide · `404` ressource absente · `413` fichier trop volumineux · `500` erreur serveur/BDD.
