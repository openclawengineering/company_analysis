#!/bin/bash

echo "=== Session End Checklist ==="
echo "Current date: $(date)"
echo ""

# Check current status
echo "1. Companies that need directories:"
companies_needing_dirs=$(tail -n +2 master_companies.csv | cut -d',' -f1 | sort -u | while IFS= read -r serial; do
    name=$(grep "^$serial," master_companies.csv | cut -d',' -f2)
    dir_name="${serial}_${name}"
    if [ ! -d "./$dir_name" ]; then
        echo "  $serial: $name"
    fi
done | wc -l)

echo "   Count: $companies_needing_dirs"

# Check companies missing company-people.json
echo ""
echo "2. Companies missing company-people.json:"
missing_people=$(find . -maxdepth 1 -type d -name "[0-9]*_*" | while IFS= read -r dir; do
    if [ ! -f "$dir/company-people.json" ]; then
        basename "$dir"
    fi
done | wc -l)

echo "   Count: $missing_people"

# Check companies missing Company Mentions
echo ""
echo "3. Companies missing Company Mentions:"
missing_mentions=$(find . -maxdepth 1 -type d -name "[0-9]*_*" | while IFS= read -r dir; do
    md_file="$dir/company-info.md"
    if [ -f "$md_file" ]; then
        if ! grep -q "## Company Mentions" "$md_file"; then
            basename "$dir"
        fi
    fi
done | wc -l)

echo "   Count: $missing_mentions"

# Final completion check
echo ""
echo "=== COMPLETION CHECK ==="
total_needs=$(($companies_needing_dirs + $missing_people + $missing_mentions))

if [ $total_needs -eq 0 ]; then
    echo "ALL_COMPANIES_COMPLETE"
else
    echo "Companies still needing work: $total_needs"
    echo "  - Need directories: $companies_needing_dirs"
    echo "  - Missing company-people.json: $missing_people" 
    echo "  - Missing Company Mentions: $missing_mentions"
fi