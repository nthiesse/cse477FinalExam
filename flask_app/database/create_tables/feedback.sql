CREATE TABLE IF NOT EXISTS feedback (
        comment_id INT(11) NOT NULL AUTO_INCREMENT COMMENT 'The comment id',
        name VARCHAR(100) NOT NULL COMMENT 'Name of the commentator',
        email VARCHAR(500) NOT NULL COMMENT 'Commentator email',
        comment VARCHAR(500) NOT NULL COMMENT 'The comment itself',
        PRIMARY KEY (comment_id)
    ) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = "Comments about the webpage";