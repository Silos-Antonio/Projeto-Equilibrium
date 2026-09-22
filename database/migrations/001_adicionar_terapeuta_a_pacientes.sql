-- Cada paciente pertence ao terapeuta que o cadastrou.
-- Execute uma vez, antes de usar as rotas de pacientes e agendamentos.
ALTER TABLE pacientes
    ADD COLUMN terapeuta_id INT NULL AFTER id,
    ADD CONSTRAINT fk_pacientes_terapeuta
        FOREIGN KEY (terapeuta_id) REFERENCES usuarios(id),
    ADD INDEX idx_paciente_terapeuta (terapeuta_id);

-- Se já houver pacientes no banco, associe-os manualmente antes de torná-los obrigatórios:
-- UPDATE pacientes SET terapeuta_id = <id_do_terapeuta> WHERE terapeuta_id IS NULL;
-- ALTER TABLE pacientes MODIFY terapeuta_id INT NOT NULL;
