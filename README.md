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

**Linux / macOS :**
```bash
cd serviceX_xxx
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Windows (PowerShell) :**
```powershell
cd serviceX_xxx
python -m venv venv ; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

**Windows (CMD) :**
```bat
cd serviceX_xxx
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Chaque service expose `GET /client` (client de test HTML, ouvrir `http://localhost:PORT/`). Voir le `README.md` de chaque service pour le détail des routes et des exemples `curl`.

> **Windows — bon à savoir :** dans PowerShell, `curl` est un alias d'`Invoke-WebRequest` (pas le vrai curl) et les guillemets simples ne délimitent pas le JSON comme sous bash. Pour tester, ouvre plutôt la page `/client` dans le navigateur, ou utilise Postman, ou installe le vrai `curl.exe` (via `winget install curl` / Git for Windows).

## Base de données MySQL (Services 3 & 4)

### ✅ Méthode recommandée — script Python (toutes plateformes)

```bash
python scripts/setup.py
```

`scripts/setup.py` rend MySQL utilisable **sans configuration manuelle** :
1. **installe MySQL** s'il est absent (winget / brew / apt) ;
2. **crée et démarre une instance MySQL locale auto-suffisante** (dossier de données dédié, hors du dépôt) — **aucun droit admin, aucun service Windows, aucun `mysql` dans le PATH** ;
3. crée la base + la table + l'utilisateur et génère les `.env`.

C'est ce qui résout les soucis classiques sous Windows (« impossible de se connecter », « mysql introuvable dans le PATH ») : le script n'a besoin que du binaire `mysqld` et gère tout le reste lui-même.

```bash
# pour viser un MySQL existant protégé par mot de passe (au lieu de l'instance locale) :
python scripts/setup.py --admin-password monmdp
```

Sous Windows, `python` peut s'appeler `py`. Le script s'auto-installe `mysql-connector-python` s'il manque. (L'**installation** de MySQL — étape 1 — peut demander une élévation UAC ; la création de l'instance locale, elle, n'en demande pas.)

> **MySQL reste allumé** une fois lancé : le script ne l'éteint jamais, `mysqld` tourne jusqu'à ce que tu fermes/redémarres le PC. **Après un redémarrage**, relance simplement `python scripts/setup.py` — c'est instantané (la base existe déjà, il ne fait que redémarrer le serveur). Si un service (3 ou 4) répond « Erreur base de données », c'est que MySQL n'est pas lancé : relance `setup.py`.

### Alternative — scripts shell

Un seul script crée la base, la table, l'utilisateur applicatif et les fichiers `.env`. Idempotent.

**Linux / macOS :**
```bash
chmod +x scripts/setup_mysql.sh
./scripts/setup_mysql.sh
# si root a un mot de passe :
MYSQL_ADMIN_PASSWORD='monmdp' ./scripts/setup_mysql.sh
```

**Windows (PowerShell) :**
```powershell
.\scripts\setup_mysql.ps1
# si root a un mot de passe :
.\scripts\setup_mysql.ps1 -MysqlAdminPassword 'monmdp'
# si l'execution de scripts est bloquee :
powershell -ExecutionPolicy Bypass -File .\scripts\setup_mysql.ps1
```
(ou double-clic sur `scripts\setup_mysql.bat`)

> **Windows — prérequis :** le client `mysql.exe` doit être dans le PATH. L'installateur MySQL ne l'ajoute pas toujours ; au besoin :
> `setx PATH "%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin"` puis rouvrir le terminal.

Variables surchargeables (bash : `VAR=...`, PowerShell : `-Param ...`) : `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `MYSQL_ADMIN`, `MYSQL_ADMIN_PASSWORD`.

**Méthode manuelle** (équivalente) : `mysql -u root < sql/init_db.sql`, puis créer un `.env` dans `service3_stats_mysql/` et `service4_csv_mysql/`.

Les identifiants sont lus depuis un fichier `.env` (jamais committé — voir `.gitignore`). Variables attendues : `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

## Tests de la partie client

Chaque service fournit, après les tests `curl`/Postman :
- un **client Python** `test_client.py` (tests unitaires `unittest`) ;
- un **client web** `test_client.html` (formulaires `fetch` JSON), servi via `GET /client`.

> **⚠️ Lancer les tests = 2 terminaux.** `test_client.py` interroge le serveur HTTP : il faut que **`python app.py` tourne déjà** dans un autre terminal (et, pour les services 3/4, que la base soit configurée via `scripts/setup.py`). Sinon le test affiche `[!] Service injoignable...`.
>
> ```
> Terminal 1 :  cd serviceX_xxx && python app.py        # laisse tourner
> Terminal 2 :  cd serviceX_xxx && python test_client.py
> ```
>
> `requests` (utilisé par les tests) est dans chaque `requirements.txt` : pense à faire `pip install -r requirements.txt` dans le venv activé.

## Workflow Git du groupe

- `main` : code testé et validé uniquement.
- `feature/sX-...` : développement d'une fonctionnalité ; `fix/sX-...` : correction de bug.
- Une **pull request** par fonctionnalité, **revue par un autre membre** avant le merge, fermeture des issues via `Closes #N`.
- Commits conventionnels : `feat(s1): ...`, `fix(s2): ...`, `test(s4): ...`, `docs(s1): ...`.

## Codes HTTP

`200` succès · `201` création (insertion) · `400` requête invalide · `404` ressource absente · `413` fichier trop volumineux · `500` erreur serveur/BDD.
