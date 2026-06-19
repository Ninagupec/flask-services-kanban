-- init_db.sql — Base et table partagees par les Services 3 et 4
-- Execution : mysql -u root < sql/init_db.sql

CREATE DATABASE IF NOT EXISTS flask_stats
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE flask_stats;

CREATE TABLE IF NOT EXISTS donnees (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nom_serie   VARCHAR(100) NOT NULL,
  valeur      DECIMAL(12,4) NOT NULL,
  categorie   VARCHAR(50) DEFAULT NULL,
  date_mesure DATE DEFAULT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Donnees de test initiales.
-- Inserees UNIQUEMENT si la table est vide -> script idempotent : on peut le
-- relancer sans dupliquer les donnees et sans ecraser ce qui a ete charge.
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
WHERE NOT EXISTS (SELECT 1 FROM donnees);
