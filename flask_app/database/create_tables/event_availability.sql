CREATE TABLE
    IF NOT EXISTS `event_availability` (
        `id` int (11) NOT NULL auto_increment COMMENT 'the id of this event',
        `user_id` varchar(255) NOT NULL COMMENT 'user of the availability',
        `event_id` int(11) COMMENT 'event correlated to this availability',
        `date` DATE NOT NULL COMMENT 'date correlated to this availability',
        `time_slot` TIME NOT NULL COMMENT 'time correlated with this',
        `availabile` varchar(300) NOT NULL COMMENT 'whether the user is available, maybe, or unavailable',
        PRIMARY KEY (`id`), UNIQUE(user_id, event_id, date, time_slot)
    ) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = "Contains site event information";