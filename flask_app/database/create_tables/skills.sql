CREATE TABLE IF NOT EXISTS skills (
        skill_id INT(11) NOT NULL AUTO_INCREMENT COMMENT 'The skill id',
        experience_id INT(11) NOT NULL COMMENT 'Experience id that links experiences and skills',
        name VARCHAR(100) NOT NULL COMMENT 'The name of the skill',
        skill_level INT(2) DEFAULT NULL COMMENT 'Level of the skill: 1 being bad and 10 being great',
        PRIMARY KEY(skill_id), FOREIGN KEY (experience_id) REFERENCES experiences(experience_id)
    ) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = "Skills I have";