--Converted to MySQL by Han 28.3

CREATE DATABASE IF NOT EXISTS resultsdb;

USE resultsdb;

CREATE TABLE IF NOT EXISTS CodeAnalysis (
  username VARCHAR(20),
  date_and_time DATETIME,
  filename VARCHAR(100),
  response_code INT,
  response TEXT,
  ai_response TEXT,
  PRIMARY KEY (username, date_and_time, filename)
);
