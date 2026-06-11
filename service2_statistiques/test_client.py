"""Client de test unitaire Python pour le Service 2.

Lance le service (python app.py) sur le port 5002, puis dans un autre
terminal : python test_client.py
Utilise le module unittest pour verifier chaque route.
"""

import unittest
import requests

BASE = "http://localhost:5002"


class TestService2(unittest.TestCase):

    def test_describe(self):
        donnees = {"data": [12.5, 15.3, 8.7, 21.0, 13.2, 9.8, 17.6, 11.4]}
        r = requests.post(f"{BASE}/stats/describe", json=donnees)
        self.assertEqual(r.status_code, 200)
        res = r.json()["resultat"]
        self.assertEqual(res["n"], 8)
        self.assertAlmostEqual(res["moyenne"], 13.6875, places=3)
        self.assertEqual(res["minimum"], 8.7)
        self.assertEqual(res["maximum"], 21.0)

    def test_correlation(self):
        donnees = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
        r = requests.post(f"{BASE}/stats/correlation", json=donnees)
        self.assertEqual(r.status_code, 200)
        res = r.json()["resultat"]
        # correlation parfaite : r = 1.0, interpretation forte
        self.assertAlmostEqual(res["r"], 1.0, places=4)
        self.assertEqual(res["interpretation"], "forte")
        self.assertTrue(res["significatif"])

    def test_test_normalite(self):
        donnees = {"data": [2.1, 2.4, 2.0, 2.6, 2.3, 2.5, 2.2, 2.4, 2.1, 2.3]}
        r = requests.post(f"{BASE}/stats/test_normalite", json=donnees)
        self.assertEqual(r.status_code, 200)
        self.assertIn("est_normale", r.json()["resultat"])

    def test_test_student(self):
        donnees = {"groupe1": [20, 22, 19, 24, 21], "groupe2": [30, 32, 29, 34, 31]}
        r = requests.post(f"{BASE}/stats/test_student", json=donnees)
        self.assertEqual(r.status_code, 200)
        res = r.json()["resultat"]
        # moyennes tres differentes -> difference significative
        self.assertTrue(res["difference_significative"])

    def test_erreur_donnees_manquantes(self):
        r = requests.post(f"{BASE}/stats/describe", json={"data": [1]})
        self.assertEqual(r.status_code, 400)
        self.assertIn("erreur", r.json())

    def test_correlation_serie_constante(self):
        # Fix #20 : une serie constante doit renvoyer 400, pas un JSON avec NaN
        donnees = {"x": [1, 2, 3, 4, 5], "y": [7, 7, 7, 7, 7]}
        r = requests.post(f"{BASE}/stats/correlation", json=donnees)
        self.assertEqual(r.status_code, 400)
        self.assertIn("variance nulle", r.json()["erreur"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
