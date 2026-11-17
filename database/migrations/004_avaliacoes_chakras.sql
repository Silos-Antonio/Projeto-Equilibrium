-- Avaliações completas e independentes do histórico de sessões.
-- Compatível com MySQL 9.1; CHECK é aplicado pelo servidor.
ALTER TABLE pacientes
    ADD CONSTRAINT uq_pacientes_terapeuta_id UNIQUE (terapeuta_id, id);

CREATE TABLE avaliacoes_chakras (
    id INT NOT NULL AUTO_INCREMENT,
    terapeuta_id INT NOT NULL,
    paciente_id INT NOT NULL,
    observacoes TEXT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_avaliacoes_chakras_paciente (terapeuta_id, paciente_id, criado_em),
    CONSTRAINT fk_avaliacoes_chakras_paciente
        FOREIGN KEY (terapeuta_id, paciente_id)
        REFERENCES pacientes (terapeuta_id, id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_avaliacoes_chakras_terapeuta
        FOREIGN KEY (terapeuta_id) REFERENCES usuarios (id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE avaliacao_chakra_itens (
    avaliacao_id INT NOT NULL,
    chakra ENUM('CORONARIO','FRONTAL','LARINGEO','CARDIACO','PLEXO_SOLAR','SACRAL','BASICO') NOT NULL,
    nivel_equilibrio TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (avaliacao_id, chakra),
    CONSTRAINT chk_avaliacao_chakra_nivel CHECK (nivel_equilibrio BETWEEN 0 AND 100),
    CONSTRAINT fk_avaliacao_chakra_itens_avaliacao
        FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes_chakras (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
