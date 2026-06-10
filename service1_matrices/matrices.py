"""Fonctions de calcul matriciel pour le Service 1.

Centralise la conversion des donnees JSON en tableaux NumPy et les
operations mathematiques sur les matrices. Garde app.py concis.
"""

import numpy as np


def parse_matrix(data, key):
    """Convertit data[key] (liste de listes) en tableau NumPy de floats.

    Leve ValueError si la cle est absente ou si le contenu n'est pas une
    matrice numerique valide.
    """
    if data is None:
        raise ValueError("Corps de requete JSON manquant")
    if key not in data:
        raise ValueError("Matrice '%s' manquante dans la requete" % key)
    try:
        matrice = np.array(data[key], dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError("Matrice '%s' invalide : %s" % (key, e))
    if matrice.ndim != 2:
        raise ValueError("Matrice '%s' invalide : doit etre une liste de listes" % key)
    return matrice


def addition(a, b):
    """Somme de deux matrices de memes dimensions."""
    if a.shape != b.shape:
        raise ValueError("Dimensions incompatibles")
    return (a + b).tolist()


def multiplication(a, b):
    """Produit matriciel A x B (colonnes de A == lignes de B)."""
    if a.shape[1] != b.shape[0]:
        raise ValueError("Colonnes(A) doit egaler Lignes(B)")
    return np.dot(a, b).tolist()


def transposee(a):
    """Transposee de la matrice A."""
    return a.T.tolist()


def determinant(a):
    """Determinant d'une matrice carree, arrondi a 6 decimales."""
    if a.shape[0] != a.shape[1]:
        raise ValueError("La matrice doit etre carree")
    return round(float(np.linalg.det(a)), 6)


def inverse(a):
    """Inverse d'une matrice carree non singuliere."""
    if a.shape[0] != a.shape[1]:
        raise ValueError("La matrice doit etre carree")
    det = np.linalg.det(a)
    if abs(det) < 1e-10:
        raise ValueError("Matrice singuliere, non inversible")
    return np.linalg.inv(a).tolist()
