CREATE TABLE IF NOT EXISTS institutions (
inst_id        INT(11)       NOT NULL AUTO_INCREMENT 	COMMENT 'The organization id',
type           VARCHAR(100)  NOT NULL                	COMMENT 'Organization Type: e.g. Academia, Industry, Government', 
name           VARCHAR(100)  NOT NULL                	COMMENT 'The name of the organization',
department     VARCHAR(100)  DEFAULT NULL            	COMMENT 'The name of the department or division',
address        VARCHAR(100)  DEFAULT NULL            	COMMENT 'The address of the institution',
city           VARCHAR(100)  DEFAULT NULL            	COMMENT 'The city of the institution.',
state          VARCHAR(100)  DEFAULT NULL            	COMMENT 'The state of the institution.',
zip            VARCHAR(10)   DEFAULT NULL            	COMMENT 'The zip of teh insititution',  
PRIMARY KEY  (inst_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Insititutions I am affiliated with";