"""Client de test unitaire Python pour le Service 4.

Prerequis : MySQL lance, base flask_stats initialisee (sql/init_db.sql),
fichier .env configure. Lancer le service (python app.py) sur le port
5004, puis : python test_client.py
"""

import io
import unittest
import requests

BASE = "http://127.0.0.1:5004"
CSV_VALIDE = (
    "nom_serie,valeur,categorie,date_mesure\n"
    "serie_test,10.0,cat,2024-02-01\n"
    "serie_test,20.0,cat,2024-02-02\n"
)


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


class TestService4(unittest.TestCase):

    def test_upload_csv_valide(self):
        files = {"file": ("data.csv", io.BytesIO(CSV_VALIDE.encode()), "text/csv")}
        r = requests.post(f"{BASE}/upload/csv", files=files)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["lignes_inserees"], 2)

    def test_colonne_valeur_manquante(self):
        csv = "nom_serie,categorie\nserie_x,cat\n"
        files = {"file": ("data.csv", io.BytesIO(csv.encode()), "text/csv")}
        r = requests.post(f"{BASE}/upload/csv", files=files)
        self.assertEqual(r.status_code, 400)
        self.assertIn("valeur", r.json()["manquantes"])

    def test_extension_non_csv(self):
        files = {"file": ("data.txt", io.BytesIO(b"x"), "text/plain")}
        r = requests.post(f"{BASE}/upload/csv", files=files)
        self.assertEqual(r.status_code, 400)

    def test_fichier_manquant(self):
        r = requests.post(f"{BASE}/upload/csv")
        self.assertEqual(r.status_code, 400)

    def test_valeurs_non_numeriques_ignorees(self):
        csv = "nom_serie,valeur\nserie_y,abc\nserie_y,5.0\n"
        files = {"file": ("data.csv", io.BytesIO(csv.encode()), "text/csv")}
        r = requests.post(f"{BASE}/upload/csv", files=files)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["lignes_inserees"], 1)
        self.assertEqual(r.json()["lignes_invalides_ignorees"], 1)

    def test_list_series(self):
        r = requests.get(f"{BASE}/upload/series")
        self.assertEqual(r.status_code, 200)
        self.assertIn("series", r.json())


if __name__ == "__main__":
    unittest.main(verbosity=2)
