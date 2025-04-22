-- Query: Score Preditivo de Promoção (Machine Learning Ready)
WITH PromotionFactors AS (
    /* CTE: Normaliza variáveis para modelo preditivo */
    SELECT 
        employee_id,
        (avg_training_score - MIN(avg_training_score) OVER ()) / 
            (MAX(avg_training_score) OVER () - MIN(avg_training_score) OVER ()) AS normalized_training,
        (previous_year_rating - AVG(previous_year_rating) OVER ()) / 
            STDDEV(previous_year_rating) OVER () AS z_rating,
        CASE 
            WHEN recruitment_channel = 'referral' THEN 1.2 
            ELSE 1.0 
        END AS channel_bonus
    FROM main_table
)
SELECT 
    m.employee_id,
    /* Fórmula: Combina fatores com pesos estratégicos */
    (0.4 * p.normalized_training + 
     0.3 * p.z_rating + 
     0.2 * (m.length_of_service/10.0) + 
     0.1 * p.channel_bonus) AS promotion_probability,
    NTILE(100) OVER (ORDER BY (0.4 * p.normalized_training + 
     0.3 * p.z_rating + 
     0.2 * (m.length_of_service/10.0) + 
     0.1 * p.channel_bonus)) AS percentile_rank
FROM main_table m
JOIN PromotionFactors p ON m.employee_id = p.employee_id
WHERE m.KPIs_met > 75;