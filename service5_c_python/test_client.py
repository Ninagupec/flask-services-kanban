"""Client de test unitaire Python pour le Service 5 (C via ctypes).

Prerequis : ./compile.sh puis python app.py (port 5005).
Puis : python test_client.py
"""

import unittest
import requests

BASE = "http://127.0.0.1:5005"
DATA = [12.5, 15.3, 8.7, 21.0, 13.2, 9.8, 17.6, 11.4]


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


class TestService5(unittest.TestCase):

    def test_health(self):
        r = requests.get(f"{BASE}/c/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["statut"], "ok")

    def test_describe(self):
        r = requests.post(f"{BASE}/c/stats/describe", json={"data": DATA})
        self.assertEqual(r.status_code, 200)
        res = r.json()["resultat"]
        self.assertAlmostEqual(res["moyenne"], 13.6875, places=3)
        self.assertEqual(res["minimum"], 8.7)
        self.assertEqual(res["maximum"], 21.0)

    def test_mean(self):
        r = requests.post(f"{BASE}/c/stats/mean", json={"data": [2, 4, 6]})
        self.assertEqual(r.status_code, 200)
        self.assertAlmostEqual(r.json()["resultat"], 4.0, places=4)

    def test_dot(self):
        r = requests.post(f"{BASE}/c/stats/dot", json={"v1": [1, 2, 3], "v2": [4, 5, 6]})
        self.assertEqual(r.status_code, 200)
        self.assertAlmostEqual(r.json()["resultat"], 32.0, places=4)

    def test_dot_longueurs_differentes(self):
        r = requests.post(f"{BASE}/c/stats/dot", json={"v1": [1, 2], "v2": [1, 2, 3]})
        self.assertEqual(r.status_code, 400)

    def test_erreur_cle_manquante(self):
        r = requests.post(f"{BASE}/c/stats/mean", json={})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
