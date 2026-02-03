import requests # type: ignore
import json
import pandas as pd # type: ignore
import time

def graphql_post (url,query,variables,headers):
    
    max_retries = 5  # Anzahl der Wiederholungen
    delay = 10  # Wartezeit zwischen den Versuchen (Sekunden)

    for attempt in range(max_retries):
        
        # Request GraphQL:
        response = requests.post(
            url,
            json={"query": query, "variables": variables}, headers=headers
        )
        
        # Evaluate response
        if response.status_code == 200:
            pretty_json = json.dumps(response.json(), indent=4 )
            data = json.loads(pretty_json)
            return data
       
        if response.status_code == 504:
            print(f"Fehler 504, Versuch {attempt+1} von {max_retries}... erneuter Versuch in {delay} Sekunden")
            time.sleep(delay)  # Warten und erneut versuchen
        else:
            break  # Erfolgreicher Request, beenden
        