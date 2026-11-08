CREATE OR REPLACE VIEW `maxa_liga_2026.zakladni_zpracovani_zapasu` AS
SELECT 
  id_zapasu, 
  kolo, 
  domaci AS tym, 
  hoste AS souper, 
  goly_domaci_zaklad AS goly_vstrelene, 
  goly_hoste_zaklad AS goly_inkasovane, 
  1 AS is_home,
  CASE 
    WHEN goly_domaci_zaklad > goly_hoste_zaklad THEN 3 
    WHEN goly_domaci_zaklad = goly_hoste_zaklad AND goly_domaci_nadstavba = 1 THEN 2 
    WHEN goly_domaci_zaklad = goly_hoste_zaklad AND goly_domaci_nadstavba = 0 THEN 1 
    ELSE 0 
  END AS body_ziskane
FROM `maxa_liga_2026.maxa_liga_2026_zapasy`
WHERE 
  stav = 'odehrano'

UNION ALL 

SELECT
  id_zapasu, 
  kolo, 
  hoste AS tym, 
  domaci AS souper, 
  goly_hoste_zaklad AS goly_vstrelene, 
  goly_domaci_zaklad AS goly_inkasovane, 
  0 AS is_home, 
  CASE 
    WHEN goly_hoste_zaklad > goly_domaci_zaklad THEN 3 
    WHEN goly_hoste_zaklad = goly_domaci_zaklad AND goly_hoste_nadstavba = 1 THEN 2 
    WHEN goly_hoste_zaklad = goly_domaci_zaklad AND goly_hoste_nadstavba = 0 THEN 1 
    ELSE 0 
  END AS body_ziskane 
FROM `maxa_liga_2026.maxa_liga_2026_zapasy` 
WHERE stav = 'odehrano'
ORDER BY id_zapasu ASC 
