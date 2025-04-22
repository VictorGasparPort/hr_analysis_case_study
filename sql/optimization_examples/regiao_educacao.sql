-- Particionamento: Segmentação por Região e Educação
CREATE TABLE main_table_partitioned PARTITION BY LIST (region, education) (
    PARTITION north_graduates VALUES IN (('North', 'Graduate')),
    PARTITION south_high_school VALUES IN (('South', 'High School')),
    PARTITION other_combinations VALUES IN (DEFAULT)
);
/* Motivo: Consultas regionais frequentemente combinam com nível educacional */