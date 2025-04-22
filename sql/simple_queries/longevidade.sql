-- Query: Análise de Longevidade (Retenção x Promoção)
/* Propósito: Identificar padrões de carreira */
SELECT 
    CASE 
        WHEN length_of_service BETWEEN 1 AND 3 THEN '1-3 anos'
        WHEN length_of_service BETWEEN 4 AND 7 THEN '4-7 anos'
        ELSE '8+ anos'
    END AS tenure_group,
    AVG(age) AS avg_age,
    AVG(is_promoted::INT) * 100 AS promotion_rate,
    COUNT(*) AS employees
FROM main_table
GROUP BY 1
ORDER BY MIN(length_of_service);