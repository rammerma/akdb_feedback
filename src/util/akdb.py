import os

token = os.getenv('AKDB_TOKEN')
if not token:
    raise ValueError("Umgebungsvariable AKDB_TOKEN ist nicht gesetzt")

headers = {
  "Authorization" : f"Bearer {token}"
}

# Die URL der GraphQL-Schnittstelle
urlV2 = 'https://www.service-digitale-verwaltung.de/mgt/v2/graphql'
urlV1 = 'https://www.service-digitale-verwaltung.de/mgt/graphql'