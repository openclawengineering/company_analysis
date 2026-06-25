#!/bin/bash

# Process batch 1: Companies 125-134 that need directories
echo "=== Processing Batch 1: Companies 125-134 ==="

# Companies to process in this batch (serial numbers)
batch_companies=(125 126 127 128 129 130 131 132 133 134)

for serial in "${batch_companies[@]}"; do
    echo "Processing company $serial..."
    
    # Get company details from CSV
    company_info=$(grep "^$serial," master_companies.csv)
    if [ -z "$company_info" ]; then
        echo "Warning: Company $serial not found in master CSV"
        continue
    fi
    
    company_name=$(echo "$company_info" | cut -d',' -f2)
    website=$(echo "$company_info" | cut -d',' -f3)
    
    dir_name="${serial}_${company_name}"
    
    # Check if directory already exists
    if [ -d "./$dir_name" ]; then
        echo "Directory $dir_name already exists, skipping directory creation"
        continue
    fi
    
    echo "Creating directory and files for $dir_name"
    
    # Create directory
    mkdir -p "$dir_name"
    
    # Create basic company-info.md
    cat > "$dir_name/company-info.md" << EOF
# ${company_name}

## Basic Information

- **Website**: [${website}](${website})
- **Serial Number**: ${serial}

## Company Overview

Company information and overview will be added here.

## Company Mentions

EOF
    
    # Create basic company-people.json
    cat > "$dir_name/company-people.json" << EOF
{
  "company": {
    "name_jp": "${company_name}",
    "name_en": "${company_name}",
    "website": "${website}"
  },
  "people": [],
  "social_profiles": [],
  "last_updated": "$(date +%Y-%m-%d)"
}
EOF
    
    echo "Created basic files for $dir_name"
    
    # Add to git
    git add "$dir_name/"
    
    echo "Added $dir_name to git staging"
    echo "---"
done

echo "=== Batch 1 completed ==="