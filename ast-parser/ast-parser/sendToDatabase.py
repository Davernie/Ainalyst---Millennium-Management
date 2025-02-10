# this makes dummy API calls and stores the result in a database

import requests
import psycopg2
from datetime import datetime
import pytz

def sendData(userName,fileLocation):
    try:
        tz = pytz.timezone("Ireland/Dublin")
        timestamp = datetime.now(tz)
        url = "http://127.0.0.1:5000/api/analyze" # suppose that is where the API will be running


        analysis = with open(fileLocation, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files)
        api_data = response.json()
        response_code = response.status_code
        conn = psycopg2.connect(database = "resultsdb", 
                                user = "AlexanderRybak", 
                                host= 'localhost',
                                port = 5432)
        cursor = conn.cursor()
        cursor.execute(
                    "INSERT INTO analysis_results (username, date_and_time, filename, response_code, response ) VALUES (%s,%s,%s, %s, %s)",
                    (userName, timestamp, fileLocation,response_code,json.dumps(api_data))
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
            return 0

