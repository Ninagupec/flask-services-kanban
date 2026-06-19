"""Fonctions de calcul matriciel pour le Service 1.

Centralise la conversion des donnees JSON en tableaux NumPy et les
operations mathematiques sur les matrices. Garde app.py concis.
"""

# NumPy : bibliotheque de calcul numerique. Elle fournit le type "tableau"
# (np.array) et les operations matricielles (produit, determinant, inverse).
import numpy as np


def parse_matrix(data, key):
    """Convertit data[key] (liste de listes) en tableau NumPy de floats.

    Leve ValueError si la cle est absente ou si le contenu n'est pas une
    matrice numerique valide.
    """
    if data is None:
        raise ValueError("Corps de requete JSON manquant")
    if key not in data:                      # ex. la cle 'A' ou 'B' est absente
        raise ValueError("Matrice '%s' manquante dans la requete" % key)
    try:
        # dtype=float force la conversion en nombres ; echoue si une valeur
        # n'est pas convertible (ex. du texte).
        matrice = np.array(data[key], dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError("Matrice '%s' invalide : %s" % (key, e))
    # ndim == 2 : une matrice est un tableau a 2 dimensions (liste de listes).
    if matrice.ndim != 2:
        raise ValueError("Matrice '%s' invalide : doit etre une liste de listes" % key)
    return matrice


def addition(a, b):
    """Somme de deux matrices de memes dimensions."""
    # .shape = (nb_lignes, nb_colonnes). L'addition exige des formes identiques.
    if a.shape != b.shape:
        raise ValueError("Dimensions incompatibles")
    # a + b additionne element par element ; .tolist() reconvertit en listes
    # Python (necessaire pour que Flask puisse renvoyer du JSON).
    return (a + b).tolist()


def multiplication(a, b):
    """Produit matriciel A x B (colonnes de A == lignes de B)."""
    # Regle du produit matriciel : le nombre de colonnes de A (shape[1]) doit
    # egaler le nombre de lignes de B (shape[0]).
    if a.shape[1] != b.shape[0]:
        raise ValueError("Colonnes(A) doit egaler Lignes(B)")
    return np.dot(a, b).tolist()             # np.dot = produit matriciel


def transposee(a):
    """Transposee de la matrice A (lignes <-> colonnes)."""
    return a.T.tolist()                      # .T = transposee en NumPy


def determinant(a):
    """Determinant d'une matrice carree, arrondi a 6 decimales."""
    # Le determinant n'existe que pour une matrice carree (autant de lignes
    # que de colonnes).
    if a.shape[0] != a.shape[1]:
        raise ValueError("La matrice doit etre carree")
    return round(float(np.linalg.det(a)), 6)  # np.linalg.det = determinant


def inverse(a):
    """Inverse d'une matrice carree non singuliere."""
    if a.shape[0] != a.shape[1]:
        raise ValueError("La matrice doit etre carree")
    det = np.linalg.det(a)
    # Si le determinant est (quasi) nul, la matrice est "singuliere" : elle n'a
    # pas d'inverse. On teste abs(det) < 1e-10 pour gerer les erreurs d'arrondi.
    if abs(det) < 1e-10:
        raise ValueError("Matrice singuliere, non inversible")
    return np.linalg.inv(a).tolist()          # np.linalg.inv = matrice inverse
