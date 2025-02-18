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

        payload = {"code": fileToAnalyze,"userName":userName,"fileLocation":fileLocation}

        response = requests.post(url, json=payload)
        response_text = response.text
        response_code = response.status_code

        print (response_code,response_text)
        return 1
    except Exception as e:
        print("Connection error:", e)
        return 0

sendData("alexrybak", "fileForTesting.py")
