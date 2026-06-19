# Service 5 (bonus) — Fonctions C appelées depuis Python (ctypes)

Service Flask qui expose en REST des fonctions de calcul statistique **écrites en C** (`src/stats.c`), compilées en bibliothèque partagée, puis appelées depuis Python via le module `ctypes`. Illustre l'optimisation utilisée par NumPy/SciPy/pandas (cœur de calcul en C).

## Compilation puis lancement

**Prérequis : `gcc` doit être installé.**
- Linux : `sudo apt install gcc`
- macOS : `xcode-select --install`
- Windows : installer **MinGW-w64** (https://www.mingw-w64.org) ou **MSYS2** (`pacman -S gcc`), puis ajouter le dossier `bin\` (contenant `gcc.exe`) au PATH.

**Linux / macOS :**
```bash
cd service5_c_python
chmod +x compile.sh && ./compile.sh        # génère lib/stats.dylib (macOS) ou lib/stats.so (Linux)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py                              # http://localhost:5005
```

**Windows (PowerShell ou CMD) :**
```bat
cd service5_c_python
compile.bat                                 :: génère lib\stats.dll (gcc MinGW)
python -m venv venv & venv\Scripts\activate
pip install -r requirements.txt
python app.py                               :: http://localhost:5005
```
> Si tu disposes de Git Bash / WSL / MSYS2 sous Windows, `bash compile.sh` fonctionne aussi (il détecte MinGW et produit `lib\stats.dll`).

> Détection d'OS : `compile.sh` choisit `-dynamiclib`+`.dylib` (macOS), `-shared`+`.so` (Linux), `-shared`+`.dll` (Windows/MinGW, sans `-fPIC` ni `-lm`). La bibliothèque compilée (`lib/*.dylib|so|dll`) **n'est pas versionnée** (voir `.gitignore`) — chaque développeur la recompile.

## Routes disponibles

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/c/stats/describe` | n, moyenne, médiane, écart-type, variance, min, max |
| POST | `/c/stats/mean` | Moyenne |
| POST | `/c/stats/stddev` | Écart-type |
| POST | `/c/stats/median` | Médiane |
| POST | `/c/stats/dot` | Produit scalaire de `v1` et `v2` |
| GET | `/c/health` | État du service |
| GET | `/client` | Client de test HTML |

## Exemples curl

```bash
curl -X POST http://localhost:5005/c/stats/describe -H 'Content-Type: application/json' \
  -d '{"data": [12.5,15.3,8.7,21.0,13.2,9.8,17.6,11.4]}'
curl -X POST http://localhost:5005/c/stats/dot -H 'Content-Type: application/json' \
  -d '{"v1": [1,2,3], "v2": [4,5,6]}'   # -> resultat 32.0
```

## Détails techniques (ctypes)

- `c_bridge.py` charge la bibliothèque (`ctypes.CDLL`) et **déclare `argtypes` / `restype`** de chaque fonction. Sans ces déclarations, ctypes suppose `int` partout → corruptions mémoire silencieuses.
- `_to_c_array()` convertit une liste Python en tableau C de `double` (`ctypes.c_double * n`) pour le passage par pointeur.

## Benchmark Python pur vs C

```bash
python benchmark.py    # compare la moyenne sur 1 000 000 valeurs
```

## Tests de la partie client

- **test_client.py** : 6 tests unitaires (`unittest`) — health, describe, mean, dot, erreurs.
- **test_client.html** : client web (`fetch` JSON), servi via `GET /client`.
