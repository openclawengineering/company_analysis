#!/bin/bash

# Get existing companies in repo (folders)
echo "Getting existing companies from repo..."
existing_folders=$(find . -maxdepth 1 -type d -name "[0-9]*_*" | sed 's|./||' | sort)

# Get companies from master CSV that have directories
master_companies_with_dirs=$(tail -n +2 master_companies.csv | cut -d',' -f1,2 | while IFS= read -r line; do
    serial=$(echo "$line" | cut -d',' -f1)
    name=$(echo "$line" | cut -d',' -f2)
    dir_name="${serial}_${name}"
    if [ -d "./$dir_name" ]; then
        echo "$serial"
    fi
done | sort -u)

# Get all master companies
all_master_companies=$(tail -n +2 master_companies.csv | cut -d',' -f1 | sort -u)

# Calculate gap
gap_count=$(($(echo "$all_master_companies" | wc -l) - $(echo "$master_companies_with_dirs" | wc -l)))

echo "=== Gap Analysis ==="
echo "Total companies in master list: $(echo "$all_master_companies" | wc -l)"
echo "Companies with directories: $(echo "$master_companies_with_dirs" | wc -l)"
echo "Companies that need directories: $gap_count"
echo ""
echo "Companies that need work (first 10):"
echo "$all_master_companies" | while read -r serial; do
    if ! echo "$master_companies_with_dirs" | grep -q "^$serial$"; then
        # Get company name from CSV
        name=$(grep "^$serial," master_companies.csv | cut -d',' -f2)
        echo "  $serial: $name"
    fi
done | head -n 10

# Check for companies that need company-people.json files
echo ""
echo "=== Checking for companies needing company-people.json ==="
companies_needing_people=$(find . -maxdepth 1 -type d -name "[0-9]*_*" | while IFS= read -r dir; do
    if [ ! -f "$dir/company-people.json" ]; then
        echo "$dir"
    fi
done)

echo "Companies missing company-people.json: $(echo "$companies_needing_people" | wc -l)"
if [ $(echo "$companies_needing_people" | wc -l) -gt 0 ]; then
    echo "First few companies needing company-people.json:"
    echo "$companies_needing_people" | head -n 5
fi

# Check for companies missing Company Mentions
echo ""
echo "=== Checking for companies missing Company Mentions ==="
companies_needing_mentions=$(find . -maxdepth 1 -type d -name "[0-9]*_*" | while IFS= read -r dir; do
    md_file="$dir/company-info.md"
    if [ -f "$md_file" ]; then
        if ! grep -q "## Company Mentions" "$md_file"; then
            echo "$dir"
        fi
    fi
done)

echo "Companies missing Company Mentions: $(echo "$companies_needing_mentions" | wc -l)"
if [ $(echo "$companies_needing_mentions" | wc -l) -gt 0 ]; then
    echo "First few companies needing Company Mentions:"
    echo "$companies_needing_mentions" | head -n 5
fi