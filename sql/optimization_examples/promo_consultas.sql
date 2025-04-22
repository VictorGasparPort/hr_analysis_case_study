-- Índice: Acelera consultas de promoção (filtro + ordenação comum)
CREATE INDEX idx_promotion_candidates ON main_table (department, is_promoted)
INCLUDE (avg_training_score, previous_year_rating)
/* Motivo: Consultas frequentes buscam promovidos por departamento com métricas específicas */
