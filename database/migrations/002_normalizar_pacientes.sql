-- Normaliza a modelagem de pacientes para o isolamento multi-tenant.
--
-- Telefone passa a ser opcional.
-- Quando informado, deve ser único dentro da carteira do terapeuta.
-- Todo paciente deve pertencer obrigatoriamente a um terapeuta.
-- Remove a antiga tabela de relacionamento, que não é mais utilizada.

ALTER TABLE pacientes
    DROP INDEX telefone;

ALTER TABLE pacientes
    MODIFY telefone VARCHAR(20) NULL;

ALTER TABLE pacientes
    DROP FOREIGN KEY fk_pacientes_terapeuta;

ALTER TABLE pacientes
    MODIFY terapeuta_id INT NOT NULL;

ALTER TABLE pacientes
    ADD CONSTRAINT fk_pacientes_terapeuta
        FOREIGN KEY (terapeuta_id)
        REFERENCES usuarios(id);

ALTER TABLE pacientes
    ADD CONSTRAINT uq_pacientes_terapeuta_telefone
        UNIQUE (terapeuta_id, telefone);

DROP TABLE terapeuta_paciente;