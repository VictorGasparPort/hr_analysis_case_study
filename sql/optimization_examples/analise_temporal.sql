-- Índice: Otimiza análise temporal de carreira
CREATE INDEX idx_career_growth ON main_table (employee_id, length_of_service)
WHERE length_of_service >= 2
/* Motivo: Foco em funcionários com +2 anos (grupo prioritário para promoções) */
