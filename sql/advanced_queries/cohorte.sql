-- Query: Análise de Cohorte por Canal de Recrutamento
SELECT 
    recruitment_cohort,
    FLOOR(length_of_service) AS service_year,
    promotion_rate,
    retention_rate
FROM (
    SELECT 
        recruitment_channel AS recruitment_cohort,
        FLOOR(length_of_service) AS service_year,
        AVG(is_promoted::INT) * 100 AS promotion_rate,
        COUNT(*) * 100.0 / MAX(total_cohort) OVER (PARTITION BY recruitment_channel) AS retention_rate
    FROM (
        SELECT *,
            COUNT(*) OVER (PARTITION BY recruitment_channel) AS total_cohort
        FROM main_table
    ) sub
    GROUP BY 1,2
) final
WHERE service_year BETWEEN 1 AND 5;
