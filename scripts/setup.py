#!/usr/bin/env python3
"""Configuration tout-en-un du projet (cross-platform : Windows / macOS / Linux).

Ce script :
  1. demarre le serveur MySQL s'il ne tourne pas deja (best effort selon l'OS) ;
  2. cree la base flask_stats + la table donnees (via sql/init_db.sql, idempotent) ;
  3. cree l'utilisateur applicatif et lui donne les droits ;
  4. genere les fichiers .env des services 3 et 4.

Il utilise mysql-connector-python (et NON le client 'mysql' en ligne de commande),
donc aucun besoin d'avoir 'mysql' dans le PATH — ideal sous Windows.

Usage :
    python scripts/setup.py
    python scripts/setup.py --admin-password monmdp     # si root a un mot de passe
    python scripts/setup.py --db-password autrechose

Options : --admin-user (def root) --admin-password --db-name (def flask_stats)
          --db-user (def flask_user) --db-password (def flask_pwd)
          --host (def 127.0.0.1) --port (def 3306) --no-start (ne pas demarrer MySQL)
"""
import argparse
import getpass
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = ROOT / "sql" / "init_db.sql"
SERVICES_AVEC_ENV = ["service3_stats_mysql", "service4_csv_mysql"]


# --- mysql-connector-python : import, avec auto-installation si absent --------
def importer_connector():
    try:
        import mysql.connector  # noqa
        return __import__("mysql.connector", fromlist=["connector"])
    except ImportError:
        print("[i] mysql-connector-python absent : installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "mysql-connector-python"], check=True)
        return __import__("mysql.connector", fromlist=["connector"])


# --- Demarrage du serveur MySQL selon l'OS -----------------------------------
def tenter_demarrage_mysql():
    systeme = platform.system()
    print(f"[i] Tentative de demarrage du serveur MySQL ({systeme})...")
    if systeme == "Windows":
        # Le nom du service depend de la version installee
        for service in ("MySQL", "MySQL80", "MySQL84", "MySQL90", "MariaDB"):
            r = subprocess.run(["net", "start", service],
                               capture_output=True, text=True)
            sortie = (r.stdout + r.stderr).lower()
            if r.returncode == 0 or "demarre" in sortie or "started" in sortie \
                    or "deja" in sortie or "already" in sortie:
                print(f"    service '{service}' OK")
                return
        print("    [!] Impossible de demarrer automatiquement (droits admin requis).")
        print("        Demarre MySQL a la main : Win+R -> services.msc -> MySQL -> Demarrer")
        print("        (ou lance ce terminal en tant qu'administrateur).")
    elif systeme == "Darwin":
        for cmd in (["brew", "services", "start", "mysql"], ["mysql.server", "start"]):
            if subprocess.run(cmd, capture_output=True, text=True).returncode == 0:
                print(f"    {' '.join(cmd)} OK")
                return
        print("    [!] Demarrage auto impossible. Essaie : brew services start mysql")
    else:  # Linux
        for cmd in (["sudo", "systemctl", "start", "mysql"],
                    ["sudo", "systemctl", "start", "mariadb"],
                    ["sudo", "service", "mysql", "start"]):
            if subprocess.run(cmd, capture_output=True, text=True).returncode == 0:
                print(f"    {' '.join(cmd)} OK")
                return
        print("    [!] Demarrage auto impossible. Essaie : sudo systemctl start mysql")


def connecter_admin(connector, args, demarrer=True):
    """Retourne une connexion admin, en demarrant MySQL au besoin."""
    def essayer(mot_de_passe):
        return connector.connect(host=args.host, port=int(args.port),
                                 user=args.admin_user, password=mot_de_passe,
                                 connection_timeout=5)

    mdp = args.admin_password
    # 1) tentative directe
    for tentative in range(2):
        try:
            return essayer(mdp if mdp is not None else "")
        except connector.Error as e:
            code = getattr(e, "errno", None)
            if code == 1045:  # mot de passe refuse
                print("[!] Acces refuse pour l'utilisateur admin.")
                mdp = getpass.getpass(f"    Mot de passe de '{args.admin_user}' : ")
                continue
            break  # autre erreur (serveur pas joignable) -> on sort de la boucle

    # 2) le serveur n'est probablement pas demarre
    if demarrer:
        tenter_demarrage_mysql()
        print("[i] Attente du serveur MySQL...")
        for _ in range(20):
            try:
                return essayer(mdp if mdp is not None else "")
            except connector.Error as e:
                if getattr(e, "errno", None) == 1045:
                    mdp = getpass.getpass(f"    Mot de passe de '{args.admin_user}' : ")
                    try:
                        return essayer(mdp)
                    except connector.Error:
                        pass
                time.sleep(1)

    print("\n[ERREUR] Connexion a MySQL impossible.")
    print("  - MySQL est-il installe et demarre ?")
    print(f"  - hote/port corrects ? ({args.host}:{args.port})")
    print("  - si root a un mot de passe : python scripts/setup.py --admin-password '...'")
    sys.exit(1)


def executer_sql_fichier(cursor, chemin):
    """Execute un fichier .sql instruction par instruction (sans le client mysql)."""
    texte = chemin.read_text(encoding="utf-8")
    # retirer les lignes de commentaire '-- ...'
    lignes = [l for l in texte.splitlines() if not l.strip().startswith("--")]
    sql = "\n".join(lignes)
    for instruction in [s.strip() for s in sql.split(";") if s.strip()]:
        cursor.execute(instruction)


def main():
    p = argparse.ArgumentParser(description="Setup MySQL + .env (cross-platform).")
    p.add_argument("--admin-user", default="root")
    p.add_argument("--admin-password", default=None)
    p.add_argument("--db-name", default="flask_stats")
    p.add_argument("--db-user", default="flask_user")
    p.add_argument("--db-password", default="flask_pwd")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", default="3306")
    p.add_argument("--no-start", action="store_true",
                   help="ne pas tenter de demarrer MySQL automatiquement")
    args = p.parse_args()

    connector = importer_connector()

    print("==> Connexion au serveur MySQL...")
    conn = connecter_admin(connector, args, demarrer=not args.no_start)
    cursor = conn.cursor()

    print("==> [1/3] Creation de la base et de la table (sql/init_db.sql)...")
    if not SQL_FILE.exists():
        print(f"[ERREUR] {SQL_FILE} introuvable."); sys.exit(1)
    executer_sql_fichier(cursor, SQL_FILE)
    conn.commit()

    print(f"==> [2/3] Utilisateur applicatif '{args.db_user}' + droits...")
    # Les identifiants ne peuvent pas etre passes en parametres -> on valide d'abord
    if not re.match(r"^[A-Za-z0-9_]+$", args.db_user) or \
       not re.match(r"^[A-Za-z0-9_]+$", args.db_name):
        print("[ERREUR] db-user et db-name : lettres, chiffres et _ uniquement."); sys.exit(1)
    cursor.execute(
        f"CREATE USER IF NOT EXISTS '{args.db_user}'@'localhost' IDENTIFIED BY %s",
        (args.db_password,))
    cursor.execute(
        f"ALTER USER '{args.db_user}'@'localhost' IDENTIFIED BY %s",
        (args.db_password,))
    cursor.execute(
        f"GRANT ALL PRIVILEGES ON `{args.db_name}`.* TO '{args.db_user}'@'localhost'")
    cursor.execute("FLUSH PRIVILEGES")
    conn.commit()

    print("==> [3/3] Generation des fichiers .env (services 3 et 4)...")
    contenu = (
        f"DB_HOST={args.host}\n"
        f"DB_PORT={args.port}\n"
        f"DB_USER={args.db_user}\n"
        f"DB_PASSWORD={args.db_password}\n"
        f"DB_NAME={args.db_name}\n"
    )
    for svc in SERVICES_AVEC_ENV:
        chemin = ROOT / svc / ".env"
        # newline="\n" -> force des fins de ligne LF meme sous Windows (compatible 3.9+)
        with open(chemin, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(contenu)
        print(f"    ecrit : {svc}/.env")

    # Verification finale
    cursor.execute(f"USE `{args.db_name}`")
    cursor.execute("SELECT nom_serie, COUNT(*) FROM donnees GROUP BY nom_serie")
    lignes = cursor.fetchall()
    cursor.close()
    conn.close()

    print("\n==> Contenu de la table 'donnees' :")
    for nom, n in lignes:
        print(f"    {nom} : {n} points")

    print(f"\nTermine. La base '{args.db_name}' est prete.")
    print("Etapes suivantes (dans chaque service a tester) :")
    print("    python -m venv venv")
    print("    Windows : venv\\Scripts\\activate      |  macOS/Linux : source venv/bin/activate")
    print("    pip install -r requirements.txt")
    print("    python app.py        # puis, dans un AUTRE terminal : python test_client.py")


if __name__ == "__main__":
    main()
