CREATE DATABASE IF NOT EXISTS touchline_demo;
USE touchline_demo;
CREATE TABLE IF NOT EXISTS teams (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(80) NOT NULL, short_name VARCHAR(5) UNIQUE NOT NULL, city VARCHAR(80));
-- CREATE
INSERT INTO teams(name,short_name,city) VALUES ('Northbridge FC','NFC','Northbridge'),('Coastal United','COU','Coast City');
-- READ
SELECT * FROM teams;
SELECT name,city FROM teams WHERE short_name='NFC';
-- UPDATE
UPDATE teams SET city='Northbridge Central' WHERE short_name='NFC';
-- DELETE demo (uncomment to execute)
-- DELETE FROM teams WHERE short_name='COU';
