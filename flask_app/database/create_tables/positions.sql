CREATE TABLE IF NOT EXISTS positions (
    position_id        INT(11)       NOT NULL AUTO_INCREMENT  COMMENT 'The position id',
    inst_id            INT(11)       NOT NULL 				  COMMENT 'FK:The instiution id',
    title              VARCHAR(100)  NOT NULL				  COMMENT 'My title in this position',
    responsibilities   VARCHAR(500)  NOT NULL                 COMMENT 'My responsibilities in this position',
    start_date         DATE          NOT NULL                 COMMENT 'My start date for this position',
    end_date           DATE          DEFAULT NULL             COMMENT 'The end date for this position',
    PRIMARY KEY (position_id),
    FOREIGN KEY (inst_id) REFERENCES institutions(inst_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Positions I have held";