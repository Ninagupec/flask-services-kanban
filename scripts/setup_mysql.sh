#!/bin/bash
#
# setup_mysql.sh — Crée et configure le serveur MySQL local du projet.
#
# Ce script est idempotent (on peut le relancer sans casser quoi que ce soit) :
#   1. crée la base flask_stats + la table donnees (via sql/init_db.sql)
#   2. crée l'utilisateur applicatif et lui donne les droits sur la base
#   3. génère les fichiers .env des services 3 et 4
#
# Prérequis : un serveur MySQL démarré localement et un compte administrateur
# (root par défaut). Le client `mysql` doit être dans le PATH.
#
# Usage :
#   chmod +x scripts/setup_mysql.sh
#   ./scripts/setup_mysql.sh
#
# Variables surchageables (valeurs par défaut entre parenthèses) :
#   DB_NAME (flask_stats)   DB_USER (flask_user)   DB_PASSWORD (flask_pwd)
#   DB_HOST (localhost)     DB_PORT (3306)
#   MYSQL_ADMIN (root)      MYSQL_ADMIN_PASSWORD (vide)
#
# Exemple avec un root protégé par mot de passe :
#   MYSQL_ADMIN_PASSWORD='monmdp' ./scripts/setup_mysql.sh

set -euo pipefail

# --- Répertoires ---------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SQL_FILE="${ROOT_DIR}/sql/init_db.sql"

# --- Paramètres (surchargeables par variables d'environnement) -----------
DB_NAME="${DB_NAME:-flask_stats}"
DB_USER="${DB_USER:-flask_user}"
DB_PASSWORD="${DB_PASSWORD:-flask_pwd}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
MYSQL_ADMIN="${MYSQL_ADMIN:-root}"
MYSQL_ADMIN_PASSWORD="${MYSQL_ADMIN_PASSWORD:-}"

# --- Construction de la commande admin -----------------------------------
ADMIN=(mysql -u "${MYSQL_ADMIN}" -h "${DB_HOST}" -P "${DB_PORT}")
if [ -n "${MYSQL_ADMIN_PASSWORD}" ]; then
    ADMIN+=("-p${MYSQL_ADMIN_PASSWORD}")
fi

echo "==> Vérification du client mysql..."
if ! command -v mysql >/dev/null 2>&1; then
    echo "ERREUR : le client 'mysql' est introuvable dans le PATH." >&2
    echo "         Installez MySQL (ex. 'brew install mysql' sur macOS) et démarrez le serveur." >&2
    exit 1
fi

echo "==> Test de connexion au serveur MySQL (${MYSQL_ADMIN}@${DB_HOST}:${DB_PORT})..."
if ! "${ADMIN[@]}" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "ERREUR : connexion impossible." >&2
    echo "         - le serveur MySQL est-il démarré ? (ex. 'brew services start mysql')" >&2
    echo "         - si root a un mot de passe : MYSQL_ADMIN_PASSWORD='...' $0" >&2
    exit 1
fi

if [ ! -f "${SQL_FILE}" ]; then
    echo "ERREUR : ${SQL_FILE} introuvable." >&2
    exit 1
fi

echo "==> [1/3] Création de la base et de la table (sql/init_db.sql)..."
"${ADMIN[@]}" < "${SQL_FILE}"

echo "==> [2/3] Création de l'utilisateur applicatif '${DB_USER}' et attribution des droits..."
"${ADMIN[@]}" <<SQL
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
ALTER USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "==> [3/3] Génération des fichiers .env (services 3 et 4)..."
for svc in service3_stats_mysql service4_csv_mysql; do
    ENV_FILE="${ROOT_DIR}/${svc}/.env"
    cat > "${ENV_FILE}" <<ENV
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
ENV
    echo "    écrit : ${svc}/.env"
done

echo ""
echo "==> Vérification finale : contenu de la table '${DB_NAME}.donnees'"
"${ADMIN[@]}" -D "${DB_NAME}" -e "SELECT nom_serie, COUNT(*) AS n_points FROM donnees GROUP BY nom_serie;"

echo ""
echo "Terminé. La base '${DB_NAME}' est prête."
echo "Lance les services 3 et 4 :"
echo "    cd service3_stats_mysql && python app.py   # port 5003"
echo "    cd service4_csv_mysql  && python app.py    # port 5004"
