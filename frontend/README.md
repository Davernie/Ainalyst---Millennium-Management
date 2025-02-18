TO SET UP FRONTEND

I. Launch database

1. Open PostgreSQL
2. Create the database
   CREATE DATABASE resultsdb;
3. Create the table
   CREATE TABLE CodeAnalysis (
   username varchar(20),
   date_and_time timestamp,
   filename varchar(100),
   response_code integer,
   response text,
   ai_response text,
   primary key (username,date_and_time,filename)
   );

II. Launch API endpoint

1. Navigate to /backend/ in Terminal
2. Run
   uvicorn main:app --reload
3. Make sure that the URL it runs on is the same one as is called in History.js and sendToDatabase.py

III. Launch React

1. Navigate to /frontend/
2. Run
   npm start
   It should be open on localhost:3000

IV. Post the file to the API (functionality not yet implemented on React)

1. Open sendToDatabase.py
2. Navigate to backend in the VSCode Terminal
3. Run the file.

V. Check the frontend on the page

1. Open
   localhost:3000
   in the browser
2. Open History
3. In Username type in alexrybak and in File Path type in fileForTesting.py
