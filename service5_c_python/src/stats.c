/* stats.c — Fonctions statistiques en C pour appel depuis Python (ctypes).
 *
 * Chaque fonction recoit un pointeur vers un tableau de double et sa taille n
 * (c'est la convention attendue par c_bridge.py). Le C ne connait pas la
 * "longueur" d'un tableau : il faut toujours la passer en parametre.
 */
#include <math.h>    /* sqrt() */
#include <stdlib.h>  /* malloc, free, qsort */
#include <string.h>  /* memcpy */

/* Moyenne arithmetique : somme des valeurs / nombre de valeurs. */
double calcul_moyenne(double *tableau, int n) {
    if (n <= 0) return 0.0;                 /* garde-fou : tableau vide */
    double somme = 0.0;
    for (int i = 0; i < n; i++) somme += tableau[i];   /* on additionne tout */
    return somme / n;
}

/* Variance (ddof=1, non biaisee) : moyenne des ecarts au carre, divisee par n-1.
 * On divise par n-1 (et non n) car on estime la variance d'un ECHANTILLON. */
double calcul_variance(double *tableau, int n) {
    if (n <= 1) return 0.0;                 /* il faut au moins 2 valeurs */
    double moyenne = calcul_moyenne(tableau, n);
    double somme_carres = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = tableau[i] - moyenne;  /* ecart a la moyenne */
        somme_carres += diff * diff;         /* eleve au carre et accumule */
    }
    return somme_carres / (n - 1);
}

/* Ecart-type = racine carree de la variance. */
double calcul_ecart_type(double *tableau, int n) {
    return sqrt(calcul_variance(tableau, n));
}

/* Fonction de comparaison utilisee par qsort pour trier des double en ordre
 * croissant. Renvoie -1, 0 ou 1 selon que a < b, a == b ou a > b. */
static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Mediane : valeur centrale d'une serie TRIEE.
 * On trie une COPIE pour ne pas modifier le tableau d'origine. */
double calcul_mediane(double *tableau, int n) {
    if (n <= 0) return 0.0;
    /* malloc reserve de la memoire pour la copie ; memcpy la remplit. */
    double *copie = (double *)malloc(n * sizeof(double));
    memcpy(copie, tableau, n * sizeof(double));
    qsort(copie, n, sizeof(double), compare_doubles);  /* tri croissant */
    double mediane;
    if (n % 2 == 0) mediane = (copie[n/2 - 1] + copie[n/2]) / 2.0;  /* pair : moyenne des 2 centraux */
    else            mediane = copie[n/2];                            /* impair : valeur du milieu */
    free(copie);                            /* on libere la memoire reservee */
    return mediane;
}

/* Minimum : on part de la 1re valeur et on garde la plus petite rencontree. */
double calcul_min(double *tableau, int n) {
    if (n <= 0) return 0.0;
    double min = tableau[0];
    for (int i = 1; i < n; i++) if (tableau[i] < min) min = tableau[i];
    return min;
}

/* Maximum : meme principe, on garde la plus grande valeur. */
double calcul_max(double *tableau, int n) {
    if (n <= 0) return 0.0;
    double max = tableau[0];
    for (int i = 1; i < n; i++) if (tableau[i] > max) max = tableau[i];
    return max;
}

/* Produit scalaire de deux vecteurs : somme des produits terme a terme
 * (v1[0]*v2[0] + v1[1]*v2[1] + ...). Les deux doivent avoir la meme taille n. */
double produit_scalaire(double *v1, double *v2, int n) {
    double resultat = 0.0;
    for (int i = 0; i < n; i++) resultat += v1[i] * v2[i];
    return resultat;
}
