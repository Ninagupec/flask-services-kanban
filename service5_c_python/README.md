# Service 5 (bonus) — Fonctions C appelées depuis Python (ctypes)

Service Flask qui expose en REST des fonctions de calcul statistique **écrites en C** (`src/stats.c`), compilées en bibliothèque partagée, puis appelées depuis Python via le module `ctypes`. Illustre l'optimisation utilisée par NumPy/SciPy/pandas (cœur de calcul en C).

## Compilation puis lancement

```bash
cd service5_c_python
chmod +x compile.sh && ./compile.sh      # génère lib/stats.dylib (.so sous Linux, .dll sous Windows)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py                            # http://localhost:5005
```

> `compile.sh` détecte l'OS : `-dynamiclib` + `.dylib` sous macOS, `-shared` + `.so`/`.dll` ailleurs. La bibliothèque compilée (`lib/*.dylib|so|dll`) **n'est pas versionnée** (voir `.gitignore`) — chaque développeur la recompile.

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
