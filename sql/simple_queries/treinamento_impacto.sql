-- Query: Impacto de Treinamentos vs. Prêmios
/* Propósito: Comparar eficácia de diferentes incentivos */
SELECT 
    CASE 
        WHEN no_of_trainings >= 3 THEN 'High Training'
        ELSE 'Normal Training'
    END AS training_group,
    CASE 
        WHEN awards_won THEN 'Awarded'
        ELSE 'Not Awarded'
    END AS award_status,
    AVG(is_promoted::INT) * 100 AS promotion_rate
FROM main_table
GROUP BY 1,2
ORDER BY 1,2;