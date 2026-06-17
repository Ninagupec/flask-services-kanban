"""Pont Python/C via ctypes pour le Service 5.

Charge la bibliotheque compilee (lib/stats.{dylib,so,dll} selon l'OS),
declare les signatures (argtypes/restype) et expose des fonctions Python
propres qui cachent la complexite ctypes.
"""

import ctypes
import os
import platform

# Determiner le nom du fichier selon le systeme
_ext = '.so'
if platform.system() == 'Darwin':
    _ext = '.dylib'
elif platform.system() == 'Windows':
    _ext = '.dll'

_lib_path = os.path.join(os.path.dirname(__file__), 'lib', f'stats{_ext}')

if not os.path.exists(_lib_path):
    raise FileNotFoundError(
        f'Bibliotheque C introuvable : {_lib_path}\n'
        'Executez ./compile.sh pour compiler src/stats.c'
    )

_lib = ctypes.CDLL(_lib_path)
_DoublePtr = ctypes.POINTER(ctypes.c_double)

# Declaration des signatures
for _nom in ('calcul_moyenne', 'calcul_variance', 'calcul_ecart_type',
             'calcul_mediane', 'calcul_min', 'calcul_max'):
    getattr(_lib, _nom).argtypes = [_DoublePtr, ctypes.c_int]
    getattr(_lib, _nom).restype = ctypes.c_double

_lib.produit_scalaire.argtypes = [_DoublePtr, _DoublePtr, ctypes.c_int]
_lib.produit_scalaire.restype = ctypes.c_double


def _to_c_array(python_list):
    """Convertit une liste Python en tableau C de doubles."""
    arr = (ctypes.c_double * len(python_list))(*python_list)
    return arr, len(python_list)


def moyenne(valeurs):
    arr, n = _to_c_array(valeurs)
    return round(_lib.calcul_moyenne(arr, n), 6)


def variance(valeurs):
    arr, n = _to_c_array(valeurs)
    return round(_lib.calcul_variance(arr, n), 6)


def ecart_type(valeurs):
    arr, n = _to_c_array(valeurs)
    return round(_lib.calcul_ecart_type(arr, n), 6)


def mediane(valeurs):
    arr, n = _to_c_array(valeurs)
    return round(_lib.calcul_mediane(arr, n), 6)


def minimum(valeurs):
    arr, n = _to_c_array(valeurs)
    return round(_lib.calcul_min(arr, n), 6)


def maximum(valeurs):
    arr, n = _to_c_array(valeurs)
    return round(_lib.calcul_max(arr, n), 6)


def dot_product(v1, v2):
    if len(v1) != len(v2):
        raise ValueError('Les deux vecteurs doivent avoir la meme longueur')
    a1, n = _to_c_array(v1)
    a2, _ = _to_c_array(v2)
    return round(_lib.produit_scalaire(a1, a2, n), 6)
