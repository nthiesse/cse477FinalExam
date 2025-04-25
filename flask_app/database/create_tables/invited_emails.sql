CREATE TABLE
    IF NOT EXISTS `invitees` (
        `invitee_id` INT AUTO_INCREMENT PRIMARY KEY,
        `event_id` INT NOT NULL,
        `email` VARCHAR(255) NOT NULL,
        FOREIGN KEY (`event_id`) REFERENCES events (`event_id`) ON DELETE CASCADE
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = "Contains each email address invited to join an event";