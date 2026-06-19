"""Client de test unitaire Python pour le Service 1.

Lancer le service (python app.py) sur le port 5001, puis dans un autre
terminal : python test_client.py
Utilise le module unittest pour verifier chaque route.
"""

import unittest
import requests

BASE = "http://127.0.0.1:5001"


def setUpModule():
    """Verifie que le service est bien demarre avant de lancer les tests."""
    try:
        requests.get(BASE, timeout=3)
    except requests.exceptions.RequestException:
        raise SystemExit(
            "[!] Service injoignable sur " + BASE
            + " -- ouvre un AUTRE terminal, active le venv, lance 'python app.py'"
            + " (laisse-le tourner), puis relance ici : python test_client.py"
        )


class TestService1(unittest.TestCase):

    def test_add(self):
        donnees = {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]}
        r = requests.post(f"{BASE}/matrices/add", json=donnees)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["resultat"], [[6.0, 8.0], [10.0, 12.0]])

    def test_multiply(self):
        donnees = {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]}
        r = requests.post(f"{BASE}/matrices/multiply", json=donnees)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["resultat"], [[19.0, 22.0], [43.0, 50.0]])

    def test_transpose(self):
        donnees = {"A": [[1, 2, 3], [4, 5, 6]]}
        r = requests.post(f"{BASE}/matrices/transpose", json=donnees)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["resultat"], [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])

    def test_determinant(self):
        donnees = {"A": [[1, 2], [3, 4]]}
        r = requests.post(f"{BASE}/matrices/determinant", json=donnees)
        self.assertEqual(r.status_code, 200)
        self.assertAlmostEqual(r.json()["resultat"], -2.0, places=4)

    def test_inverse(self):
        donnees = {"A": [[4, 7], [2, 6]]}
        r = requests.post(f"{BASE}/matrices/inverse", json=donnees)
        self.assertEqual(r.status_code, 200)
        res = r.json()["resultat"]
        self.assertAlmostEqual(res[0][0], 0.6, places=4)
        self.assertAlmostEqual(res[1][1], 0.4, places=4)

    def test_inverse_singuliere(self):
        # matrice singuliere -> erreur 400
        donnees = {"A": [[1, 2], [2, 4]]}
        r = requests.post(f"{BASE}/matrices/inverse", json=donnees)
        self.assertEqual(r.status_code, 400)
        self.assertIn("erreur", r.json())

    def test_add_dimensions_incompatibles(self):
        donnees = {"A": [[1, 2]], "B": [[1, 2], [3, 4]]}
        r = requests.post(f"{BASE}/matrices/add", json=donnees)
        self.assertEqual(r.status_code, 400)
        self.assertIn("erreur", r.json())


if __name__ == "__main__":
    unittest.main(verbosity=2)
