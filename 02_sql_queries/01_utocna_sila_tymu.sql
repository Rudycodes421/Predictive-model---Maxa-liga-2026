CREATE OR REPLACE VIEW `maxa_liga_2026.utocna_sila_tymu` AS 
WITH tym_prumery AS (
  SELECT 
    kolo, 
    tym, 
    souper, 
    goly_vstrelene, 
    AVG(goly_inkasovane) OVER(
      PARTITION BY souper ORDER BY kolo ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING 
    ) AS prumer_inkasovane_goly_souper
  FROM `maxa_liga_2026.zakladni_zpracovani_zapasu`
)
SELECT
  tym, 
  ROUND(AVG(goly_vstrelene/COALESCE(NULLIF(prumer_inkasovane_goly_souper,0), 2.7)), 4) AS upravena_utocna_sila 
FROM tym_prumery
GROUP BY
  tym
ORDER BY
  upravena_utocna_sila DESC;