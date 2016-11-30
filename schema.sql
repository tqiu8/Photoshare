
CREATE DATABASE photoshare;
USE photoshare;
DROP TABLE Likes;


CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    first_name varchar(20) NOT NULL,
    last_name varchar(20) NOT NULL,
    dob date,
    hometown varchar(20),
    gender CHAR(3),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
) ENGINE=INNODB;

CREATE TABLE Friends(
    user_1 int4 NOT NULL,
	user_2 int4 NOT NULL,
	CONSTRAINT friends_pk PRIMARY KEY (user_1, user_2)
) ENGINE=INNODB;

CREATE TABLE Albums(
	album_id int4 AUTO_INCREMENT,
	name varchar(20) NOT NULL,
	date date,
	user_id int4,
	CONSTRAINT albums_pk PRIMARY KEY (album_id)
) ENGINE=INNODB;
	
CREATE TABLE Pictures(
	picture_id int4 AUTO_INCREMENT,
	user_id int4,
	imgdata longblob ,
	caption VARCHAR(255),
	album_id int4,
	INDEX upid_idx (user_id),
	CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
) ENGINE=INNODB;

CREATE TABLE Comments(
	comment_id int4 AUTO_INCREMENT,
	user_id int4,
	picture_id int4,
	text VARCHAR(255),
	date date,
	CONSTRAINT comments_pk PRIMARY KEY (comment_id)
) ENGINE=INNODB;

CREATE TABLE Tags(
	word varchar(255) NOT NULL,
	picture_id int4
) ENGINE=INNODB;

CREATE TABLE Likes(
	user_id int4,
	picture_id int4,
	CONSTRAINT like_pk PRIMARY KEY (user_id, picture_id)
) ENGINE=INNODB; 

INSERT INTO Users (email, password, first_name, last_name) VALUES ('test@bu.edu', 'test', 'Tammy', 'Qiu');
INSERT INTO Users (email, password, first_name, last_name) VALUES ('test1@bu.edu', 'test', 'Tammy', 'Qiu');
