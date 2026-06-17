/* stats.c — Fonctions statistiques en C pour appel depuis Python (ctypes) */
#include <math.h>
#include <stdlib.h>
#include <string.h>

/* Moyenne arithmetique */
double calcul_moyenne(double *tableau, int n) {
    if (n <= 0) return 0.0;
    double somme = 0.0;
    for (int i = 0; i < n; i++) somme += tableau[i];
    return somme / n;
}

/* Variance (ddof=1, non biaisee) */
double calcul_variance(double *tableau, int n) {
    if (n <= 1) return 0.0;
    double moyenne = calcul_moyenne(tableau, n);
    double somme_carres = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = tableau[i] - moyenne;
        somme_carres += diff * diff;
    }
    return somme_carres / (n - 1);
}

/* Ecart-type */
double calcul_ecart_type(double *tableau, int n) {
    return sqrt(calcul_variance(tableau, n));
}

/* Mediane (tri interne sur une copie) */
static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

double calcul_mediane(double *tableau, int n) {
    if (n <= 0) return 0.0;
    double *copie = (double *)malloc(n * sizeof(double));
    memcpy(copie, tableau, n * sizeof(double));
    qsort(copie, n, sizeof(double), compare_doubles);
    double mediane;
    if (n % 2 == 0) mediane = (copie[n/2 - 1] + copie[n/2]) / 2.0;
    else            mediane = copie[n/2];
    free(copie);
    return mediane;
}

/* Minimum */
double calcul_min(double *tableau, int n) {
    if (n <= 0) return 0.0;
    double min = tableau[0];
    for (int i = 1; i < n; i++) if (tableau[i] < min) min = tableau[i];
    return min;
}

/* Maximum */
double calcul_max(double *tableau, int n) {
    if (n <= 0) return 0.0;
    double max = tableau[0];
    for (int i = 1; i < n; i++) if (tableau[i] > max) max = tableau[i];
    return max;
}

/* Produit scalaire de deux vecteurs */
double produit_scalaire(double *v1, double *v2, int n) {
    double resultat = 0.0;
    for (int i = 0; i < n; i++) resultat += v1[i] * v2[i];
    return resultat;
}
