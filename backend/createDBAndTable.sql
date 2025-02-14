-- code to create the table in PostgreSQL

CREATE TABLE CodeAnalysis (
username varchar(20),
date_and_time timestamp,
filename varchar(100),
response_code integer,
response text,
ai_response text,
primary key (username,date_and_time,filename)
);