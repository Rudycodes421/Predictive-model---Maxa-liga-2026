CREATE OR REPLACE VIEW `maxa_liga_2026.obranna_sila_tymu` AS
WITH tym_prumery AS (
  SELECT 
    kolo, 
    tym,
    souper,
    goly_inkasovane,
    AVG(goly_vstrelene) OVER(
      PARTITION BY souper ORDER BY kolo ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING 
    ) AS prumer_vstrelene_goly_souper
  FROM `maxa_liga_2026.zakladni_zpracovani_zapasu`
)
SELECT 
  tym,
  ROUND(AVG(goly_inkasovane/COALESCE(NULLIF(prumer_vstrelene_goly_souper,0),2.7)),4) AS upravena_obranna_sila
FROM tym_prumery
GROUP BY 
  tym
ORDER BY 
  upravena_obranna_sila ASC; 
