"""Pont Python/C via ctypes pour le Service 5.

Charge la bibliotheque compilee (lib/stats.{dylib,so,dll} selon l'OS),
declare les signatures (argtypes/restype) et expose des fonctions Python
propres qui cachent la complexite ctypes.
"""

import ctypes      # module standard pour appeler du code C compile depuis Python
import os
import platform    # pour detecter le systeme d'exploitation

# La bibliotheque compilee n'a pas la meme extension selon l'OS :
# Linux -> .so, macOS -> .dylib, Windows -> .dll.
_ext = '.so'
if platform.system() == 'Darwin':       # Darwin = macOS
    _ext = '.dylib'
elif platform.system() == 'Windows':
    _ext = '.dll'

# Chemin vers la bibliotheque dans le dossier lib/.
_lib_path = os.path.join(os.path.dirname(__file__), 'lib', f'stats{_ext}')

# Si elle n'existe pas, c'est qu'on n'a pas encore compile stats.c -> message d'aide.
if not os.path.exists(_lib_path):
    if platform.system() == 'Windows':
        _hint = 'Executez : compile.bat (ou "bash compile.sh" sous Git Bash/WSL/MSYS2)'
    else:
        _hint = 'Executez : ./compile.sh'
    raise FileNotFoundError(
        f'Bibliotheque C introuvable : {_lib_path}\n{_hint}'
    )

# CDLL charge la bibliotheque C en memoire ; ses fonctions deviennent appelables.
_lib = ctypes.CDLL(_lib_path)
# Type "pointeur vers double" : c'est ainsi qu'on passe un tableau a une fonction C.
_DoublePtr = ctypes.POINTER(ctypes.c_double)

# Declaration des signatures : on dit a ctypes le TYPE des arguments (argtypes) et
# du retour (restype) de chaque fonction C. SANS ca, ctypes suppose des int et
# corromprait silencieusement les calculs sur des double.
for _nom in ('calcul_moyenne', 'calcul_variance', 'calcul_ecart_type',
             'calcul_mediane', 'calcul_min', 'calcul_max'):
    getattr(_lib, _nom).argtypes = [_DoublePtr, ctypes.c_int]  # (tableau, taille)
    getattr(_lib, _nom).restype = ctypes.c_double              # retourne un double

# Le produit scalaire prend DEUX tableaux + leur taille.
_lib.produit_scalaire.argtypes = [_DoublePtr, _DoublePtr, ctypes.c_int]
_lib.produit_scalaire.restype = ctypes.c_double


def _to_c_array(python_list):
    """Convertit une liste Python en tableau C de doubles."""
    # (ctypes.c_double * n)(*liste) cree un tableau C de n doubles initialise
    # avec les valeurs de la liste. On renvoie le tableau ET sa taille.
    arr = (ctypes.c_double * len(python_list))(*python_list)
    return arr, len(python_list)


# Fonctions "propres" : elles convertissent la liste, appellent la fonction C
# correspondante, et arrondissent le resultat. L'utilisateur ne voit pas ctypes.
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
    # Le produit scalaire n'a de sens que pour deux vecteurs de meme longueur.
    if len(v1) != len(v2):
        raise ValueError('Les deux vecteurs doivent avoir la meme longueur')
    a1, n = _to_c_array(v1)
    a2, _ = _to_c_array(v2)
    return round(_lib.produit_scalaire(a1, a2, n), 6)
