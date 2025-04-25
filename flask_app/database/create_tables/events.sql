CREATE TABLE
    IF NOT EXISTS `events` (
        `event_id` int (11) NOT NULL auto_increment COMMENT 'the id of this event',
        `event_name` varchar(300) NOT NULL COMMENT 'name of event',
        `start_date` DATE NOT NULL COMMENT 'start date of the event',
        `end_date` DATE NOT NULL COMMENT 'end date of the event',
        `start_time` TIME NOT NULL COMMENT 'start time of the event',
        `end_time` TIME NOT NULL COMMENT 'end time of the event',
        `event_creator` varchar(300) NOT NULL COMMENT 'person who created this event',
        PRIMARY KEY (`event_id`)
    ) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = "Contains site event information";