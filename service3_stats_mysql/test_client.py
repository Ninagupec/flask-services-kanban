"""Client de test unitaire Python pour le Service 3 (stats depuis MySQL).

Prerequis : MySQL lance, base flask_stats initialisee (sql/init_db.sql),
fichier .env configure. Lancer le service (python app.py, port 5003),
puis : python test_client.py
"""

import unittest
import requests

BASE = "http://127.0.0.1:5003"


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


class TestService3(unittest.TestCase):

    def test_describe(self):
        r = requests.get(f"{BASE}/db/stats/describe", params={"serie": "serie_A"})
        self.assertEqual(r.status_code, 200)
        res = r.json()["resultat"]
        self.assertEqual(res["serie"], "serie_A")
        self.assertGreaterEqual(res["n"], 1)
        self.assertIn("moyenne", res)

    def test_describe_serie_inexistante(self):
        r = requests.get(f"{BASE}/db/stats/describe", params={"serie": "inexistante"})
        self.assertEqual(r.status_code, 404)
        self.assertIn("erreur", r.json())

    def test_describe_parametre_manquant(self):
        r = requests.get(f"{BASE}/db/stats/describe")
        self.assertEqual(r.status_code, 400)

    def test_correlation(self):
        r = requests.get(f"{BASE}/db/stats/correlation",
                         params={"serie_x": "serie_A", "serie_y": "serie_B"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("r", r.json()["resultat"])

    def test_correlation_parametre_manquant(self):
        r = requests.get(f"{BASE}/db/stats/correlation", params={"serie_x": "serie_A"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
