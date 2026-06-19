-- init_db.sql — Base et table partagees par les Services 3 et 4
-- Execution : mysql -u root < sql/init_db.sql

-- Cree la base "flask_stats" si elle n'existe pas deja.
-- utf8mb4 = jeu de caracteres complet (gere les accents et emojis).
CREATE DATABASE IF NOT EXISTS flask_stats
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- On selectionne cette base : les commandes suivantes s'y appliquent.
USE flask_stats;

-- Table qui stocke toutes les mesures. Une ligne = une valeur d'une serie.
CREATE TABLE IF NOT EXISTS donnees (
  id          INT AUTO_INCREMENT PRIMARY KEY,   -- identifiant unique auto-incremente
  nom_serie   VARCHAR(100) NOT NULL,            -- nom de la serie (ex. 'serie_A'), obligatoire
  valeur      DECIMAL(12,4) NOT NULL,           -- valeur numerique (4 decimales), obligatoire
  categorie   VARCHAR(50) DEFAULT NULL,         -- categorie facultative (ex. 'temperature')
  date_mesure DATE DEFAULT NULL,                -- date de la mesure (facultative)
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- date d'insertion, remplie automatiquement
);

-- Donnees de test initiales.
-- Inserees UNIQUEMENT si la table est vide -> script idempotent : on peut le
-- relancer sans dupliquer les donnees et sans ecraser ce qui a ete charge.
-- Technique : on construit les lignes avec des SELECT ... UNION ALL, et le
-- WHERE NOT EXISTS bloque l'insertion si la table contient deja au moins 1 ligne.
INSERT INTO donnees (nom_serie, valeur, categorie, date_mesure)
SELECT * FROM (
  SELECT 'serie_A' AS nom_serie, 12.50 AS valeur, 'temperature' AS categorie, '2024-01-15' AS date_mesure
  UNION ALL SELECT 'serie_A', 15.30, 'temperature', '2024-01-16'
  UNION ALL SELECT 'serie_A',  8.70, 'temperature', '2024-01-17'
  UNION ALL SELECT 'serie_A', 21.00, 'temperature', '2024-01-18'
  UNION ALL SELECT 'serie_A', 13.20, 'temperature', '2024-01-19'
  UNION ALL SELECT 'serie_B', 45.10, 'pression', '2024-01-15'
  UNION ALL SELECT 'serie_B', 52.80, 'pression', '2024-01-16'
  UNION ALL SELECT 'serie_B', 48.60, 'pression', '2024-01-17'
  UNION ALL SELECT 'serie_B', 55.20, 'pression', '2024-01-18'
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM donnees);   -- n'insere que si la table est vide
