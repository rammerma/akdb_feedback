#!/bin/bash

# Export Feedback in Ausländerwesen mode
cd "$(dirname "$0")/.."
python3 src/main.py

echo "Feedback data export completed."

# echo "Copying output files to OneDrive..."

# echo $(ls -ld ~/OneDrive\ -\ moysies\ \&\ partners\ GmbH/P-101-01\ OZG\ BB/03_Projektarbeit/temp/)

# cp outputFeedbacksAuslaenderwesen_a* ~/OneDrive\ -\ moysies\ \&\ partners\ GmbH/P-101-01\ OZG\ BB/03_Projektarbeit/temp/

# ls -ld ~/OneDrive\ -\ moysies\ \&\ partners\ GmbH/P-101-01\ OZG\ BB/03_Projektarbeit/temp/