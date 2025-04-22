-- Query: Detecção de Viés em Promoções (Análise de Equidade)
SELECT 
    gender,
    education,
    department,
    observed_promotion_rate,
    expected_promotion_rate,
    (observed_promotion_rate - expected_promotion_rate) AS promotion_gap,
    CASE 
        WHEN ABS(observed_promotion_rate - expected_promotion_rate) > 2 * std_dev THEN 'Significativo'
        ELSE 'Dentro do Esperado'
    END AS gap_status
FROM (
    SELECT 
        gender,
        education,
        department,
        /* Taxa de promoção observada */
        AVG(is_promoted::INT) * 100 AS observed_promotion_rate,
        /* Taxa esperada baseada na média departamental */
        (SELECT AVG(is_promoted::INT) * 100 FROM main_table m2 WHERE m2.department = m1.department) AS expected_promotion_rate,
        /* Desvio padrão histórico do departamento */
        (SELECT STDDEV(is_promoted::INT) * 100 FROM main_table m3 WHERE m3.department = m1.department) AS std_dev
    FROM main_table m1
    GROUP BY gender, education, department
) analysis
WHERE observed_promotion_rate IS NOT NULL;