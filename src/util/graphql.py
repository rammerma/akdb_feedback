import requests # type: ignore
import json
import argparse
import pandas as pd # type: ignore
import queries

# Die URL der GraphQL-Schnittstelle
urlV2 = 'https://www.service-digitale-verwaltung.de/mgt/v2/graphql'
urlV1 = 'https://www.service-digitale-verwaltung.de/mgt/graphql'

# Befehlszeilen-Parser konfigurieren
parser = argparse.ArgumentParser(description='GraphQL Request mit Befehlszeilenvariable')
parser.add_argument('--mode', type=str, required=True, help='Was willste denn?')
parser.add_argument('--searchString', type=str, required=False, help='Ein Suchstring für das Auffinden von Kommunen-Konfigurationen')

# Argumente parsen
args = parser.parse_args()
mode = args.mode
searchString = args.searchString


if (mode == "searchCommune"):
    queries.searchCommune(urlV1,searchString)
elif (mode == "exportFeedback") :
    queries.exportFeedback(urlV2)
elif (mode == "exportFeedbackCount"):
    queries.exportFeedbackStatistics(urlV1)
elif (mode == "exportActivities"):
    queries.exportActivities(urlV1)