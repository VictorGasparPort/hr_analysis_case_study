-- Tabela: Benchmark Departamental (Compara métricas entre departamentos)
CREATE TABLE department_benchmarks (
    department VARCHAR(50) PRIMARY KEY,
    avg_promotion_rate NUMERIC(5,2),
    top_recruitment_channel VARCHAR(50),
    avg_training_effectiveness NUMERIC(5,2)
);
/* Propósito: Facilitar comparações de performance entre departamentos */
INSERT INTO department_benchmarks
SELECT 
    department,
    AVG(CASE WHEN is_promoted THEN 1.0 ELSE 0.0 END) * 100 AS avg_promotion_rate,
    MODE() WITHIN GROUP (ORDER BY recruitment_channel) AS top_recruitment_channel,
    AVG(avg_training_score) FILTER (WHERE no_of_trainings > 0) AS avg_training_effectiveness
FROM main_table
GROUP BY department;