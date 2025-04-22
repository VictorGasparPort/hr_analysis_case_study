-- Query: Taxa de Promoção por Departamento (Dashboard RH)
/* Propósito: Monitoramento básico de desempenho organizacional */
SELECT 
    department,
    COUNT(*) FILTER (WHERE is_promoted) AS promotions,
    ROUND(AVG(previous_year_rating), 1) AS avg_rating,
    COUNT(*) AS total_employees,
    ROUND(COUNT(*) FILTER (WHERE is_promoted) * 100.0 / COUNT(*), 2) AS promotion_rate
FROM main_table
GROUP BY department
ORDER BY promotion_rate DESC;
