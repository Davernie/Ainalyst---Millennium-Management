import ssl
import requests
import psycopg2
from datetime import datetime
from pytz import utc

def sendData(userName, fileLocation):
    try:
        timestamp = datetime.now(utc)
        url = "http://127.0.0.1:8000/analyze/"  # suppose that is where the API will be running

        with open(fileLocation, "r") as file:
            fileToAnalyze = file.read()

        payload = {"code": fileToAnalyze}

        response = requests.post(url, json=payload)
        response_text = response.text
        response_code = response.status_code

        try:
            conn = psycopg2.connect(database="resultsdb",
                                    host='localhost',
                                    port=5432)
            cursor = conn.cursor()
            if response_code == 200:
                cursor.execute(
                    "INSERT INTO CodeAnalysis (username, date_and_time, filename, response_code, response, ai_response) VALUES (%s, %s, %s, %s, %s, %s)",
                    (userName, timestamp, fileLocation, response_code, response_text, "Not yet implemented")
                )
            elif response_code == 204:
                cursor.execute(
                    "INSERT INTO CodeAnalysis (username, date_and_time, filename, response_code, response, ai_response) VALUES (%s, %s, %s, %s, %s, %s)",
                    (userName, timestamp, fileLocation, response_code, "No issues detected", "Not yet implemented")
                )
            else:
                cursor.execute(
                    "INSERT INTO CodeAnalysis (username, date_and_time, filename, response_code, response, ai_response) VALUES (%s, %s, %s, %s, %s, %s)",
                    (userName, timestamp, fileLocation, response_code, "API error", "Not yet implemented")
                )
            conn.commit()
            print("API response successfully stored in PostgreSQL!")
        except Exception as e:
            print("Database error:", e)
        finally:
            cursor.close()
            conn.close()
        return 1
    except Exception as e:
        print("Connection error:", e)
        return 0

sendData("alexrybak", "ast_parser/fileForTesting.py")
