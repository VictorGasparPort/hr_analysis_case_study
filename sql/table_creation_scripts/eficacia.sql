-- Tabela: Eficácia de Treinamentos (Analisa ROI de programas de treinamento)
CREATE TABLE training_impact AS
/* Propósito: Medir impacto real dos treinamentos nas promoções */
SELECT 
    no_of_trainings,
    AVG(avg_training_score) AS score_avg,
    COUNT(*) FILTER (WHERE is_promoted) * 100.0 / COUNT(*) AS promotion_rate,
    CORR(no_of_trainings, previous_year_rating) AS training_rating_correlation
FROM main_table
GROUP BY no_of_trainings;