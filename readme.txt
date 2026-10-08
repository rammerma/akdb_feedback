Der AKDB-Token wird aus der lokalen Datei `.env` geladen:

AKDB_TOKEN="eyJ0e..."

Die Datei `.env` ist von Git ausgeschlossen und darf nicht eingecheckt
oder weitergegeben werden. Eine bereits gesetzte Umgebungsvariable
`AKDB_TOKEN` hat Vorrang vor dem Wert aus `.env`.

Ausführung aus dem übergeordneten Projektverzeichnis:

./exportAWfeedback.sh
