# Service 2 — Fonctions statistiques (Etudiant B)

API REST Flask qui calcule des statistiques sur des series de nombres
envoyees en JSON. Port : **5002**. Technologies : Flask, NumPy, SciPy.

## Installation

```bash
cd service2_statistiques
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # demarre sur http://localhost:5002
```

## Routes

| Methode | Route                     | Description                                   |
|---------|---------------------------|-----------------------------------------------|
| POST    | `/stats/describe`         | Statistiques descriptives d'une serie         |
| POST    | `/stats/correlation`      | Correlation de Pearson entre `x` et `y`       |
| POST    | `/stats/test_normalite`   | Test de normalite de Shapiro-Wilk             |
| POST    | `/stats/test_student`     | Test t de Student entre `groupe1` et `groupe2`|

### Exemples de requetes

```bash
# Description
curl -X POST http://localhost:5002/stats/describe \
     -H 'Content-Type: application/json' \
     -d '{"data": [12.5, 15.3, 8.7, 21.0, 13.2, 9.8, 17.6, 11.4]}'

# Correlation
curl -X POST http://localhost:5002/stats/correlation \
     -H 'Content-Type: application/json' \
     -d '{"x": [1,2,3,4,5], "y": [2,4,6,8,10]}'

# Test de normalite
curl -X POST http://localhost:5002/stats/test_normalite \
     -H 'Content-Type: application/json' \
     -d '{"data": [2.1,2.4,2.0,2.6,2.3,2.5,2.2,2.4,2.1,2.3]}'

# Test t de Student
curl -X POST http://localhost:5002/stats/test_student \
     -H 'Content-Type: application/json' \
     -d '{"groupe1": [20,22,19,24,21], "groupe2": [30,32,29,34,31]}'
```

## Tests de la partie client

- **Python** (`test_client.py`) : tests unitaires `unittest` qui appellent chaque route et verifient les resultats.
  ```bash
  pip install requests
  python test_client.py
  ```
- **HTML/JS** (`test_client.html`) : page a ouvrir dans un navigateur, avec un formulaire par route qui envoie une requete `fetch` et affiche la reponse JSON.

## Gestion des erreurs

- Liste de moins de 2 valeurs, cle manquante ou corps JSON absent -> `400` avec un champ `erreur`.
- `x` et `y` de longueurs differentes -> `400`.
- Shapiro-Wilk limite a 5000 valeurs -> `400` au-dela.
