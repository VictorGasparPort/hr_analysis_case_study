-- Tabela : Elegibilidade para Promoção (Armazena métricas-chave para análise de promoções)
CREATE TABLE promotion_eligibility AS
/* Propósito: Centralizar indicadores críticos para decisões de promoção */
SELECT 
    employee_id,
    department,
    previous_year_rating,
    CASE 
        WHEN KPIs_met > 80 AND awards_won THEN 'High Potential'
        WHEN KPIs_met > 80 OR awards_won THEN 'Medium Potential'
        ELSE 'Review Needed'
    END AS potential_category,
    avg_training_score,
    (no_of_trainings * 0.3 + previous_year_rating * 0.5 + length_of_service * 0.2) AS promotion_score
FROM main_table
WHERE length_of_service >= 1;  -- Exclui novos contratados sem histórico completo