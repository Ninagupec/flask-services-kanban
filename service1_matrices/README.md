# Service 1 — Calculs matriciels

API REST Flask pour effectuer des opérations mathématiques sur des matrices, à l'aide de NumPy.

## Installation

```bash
cd service1_matrices
python -m venv venv && source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
python app.py        # le service écoute sur http://localhost:5001
```

## Routes disponibles

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/matrices/add` | Addition de deux matrices de mêmes dimensions |
| POST | `/matrices/multiply` | Produit matriciel A × B |
| POST | `/matrices/transpose` | Transposée de A |
| POST | `/matrices/determinant` | Déterminant d'une matrice carrée |
| POST | `/matrices/inverse` | Inverse d'une matrice carrée non singulière |
| GET | `/client` | Client de test HTML |

### POST /matrices/add
Corps : `{"A": [[1,2],[3,4]], "B": [[5,6],[7,8]]}`
Réponse 200 : `{"operation": "addition", "resultat": [[6.0,8.0],[10.0,12.0]]}`
Erreur 400 si les dimensions sont incompatibles.

### POST /matrices/multiply
Corps : `{"A": [[1,2],[3,4]], "B": [[5,6],[7,8]]}`
Erreur 400 si `colonnes(A) != lignes(B)`.

### POST /matrices/transpose
Corps : `{"A": [[1,2,3],[4,5,6]]}`

### POST /matrices/determinant
Corps : `{"A": [[1,2],[3,4]]}` → `{"resultat": -2.0}`. Erreur 400 si la matrice n'est pas carrée.

### POST /matrices/inverse
Corps : `{"A": [[4,7],[2,6]]}`. Erreur 400 si la matrice est singulière (déterminant ≈ 0).

## Exemples curl

```bash
curl -X POST http://localhost:5001/matrices/add \
  -H 'Content-Type: application/json' \
  -d '{"A": [[1,2],[3,4]], "B": [[5,6],[7,8]]}'

curl -X POST http://localhost:5001/matrices/multiply \
  -H 'Content-Type: application/json' \
  -d '{"A": [[1,2,3],[4,5,6],[7,8,10]], "B": [[1,0,0],[0,1,0],[0,0,1]]}'
```

## Tests de la partie client

- **test_client.py** : tests unitaires Python (`unittest`) couvrant les 5 routes + cas d'erreur (matrice singulière, dimensions incompatibles). Lancer le service puis `python test_client.py`.
- **test_client.html** : page web (un formulaire par route) servie via `GET /client`, qui envoie des requêtes `fetch` JSON et affiche la réponse.

## Codes HTTP

| Code | Quand |
|------|-------|
| 200 | Calcul réussi |
| 400 | JSON invalide, matrice manquante, dimensions incompatibles, matrice non carrée ou singulière |
