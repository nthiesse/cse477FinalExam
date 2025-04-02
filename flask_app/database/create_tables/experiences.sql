CREATE TABLE IF NOT EXISTS experiences (
  experience_id   INT(11)       NOT NULL AUTO_INCREMENT  COMMENT 'The experience id',
  position_id     INT(11)       NOT NULL                COMMENT 'The associated position id',
  name            VARCHAR(255)  NOT NULL                COMMENT 'The name of the experience',
  description     TEXT          DEFAULT NULL            COMMENT 'Description of the experience',
  hyperlink       VARCHAR(500)  DEFAULT NULL            COMMENT 'Optional hyperlink to more information',
  start_date      DATE          DEFAULT NULL            COMMENT 'Start date of the experience',
  end_date        DATE          DEFAULT NULL            COMMENT 'End date of the experience',
  PRIMARY KEY (experience_id),
  FOREIGN KEY (position_id) REFERENCES positions(position_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='Experiences associated with positions';


