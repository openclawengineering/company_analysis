#!/bin/bash

# Download the master CSV from the gist
curl -s "https://gist.githubusercontent.com/hazrat-arisaftech/2dc68f7845553be258733cafa2cff7db/raw/64ae5f8f1a8778371e6d9032d9ab6c244b13d60d/gistfile1.txt" > master_companies.csv

# Count the total number of companies (subtracting header)
total_companies=$(($(wc -l < master_companies.csv) - 1))

echo "Master CSV downloaded successfully."
echo "Total companies in master list: $total_companies"
echo "First few companies:"
head -n 11 master_companies.csv