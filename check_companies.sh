#!/bin/bash

# Script to check which companies in companies_to_process.txt actually need processing
COMpanies_TO_PROCESS="/home/openclaw_user/.openclaw/workspace/companies_to_process.txt"
COMPANY_ANALYSIS_DIR="/home/openclaw_user/.openclaw/workspace/company_analysis"

echo "Checking companies that need processing..."
echo "================================================"

# Count total companies
TOTAL=$(wc -l < "$COMpanies_TO_PROCESS")
echo "Total companies in to_process list: $TOTAL"

# Initialize counters
NEED_PROCESSING=0
ALREADY_DONE=0
MISSING_DIR=0
MISSING_FILES=0
MISSING_MENTIONS=0

# Read each company and check its status
while IFS= read -r company_path; do
    # Extract just the company name (remove company_analysis/ prefix)
    company_name=$(echo "$company_path" | sed 's|company_analysis/||')
    
    if [ ! -d "$COMPANY_ANALYSIS_DIR/$company_name" ]; then
        echo "❌ MISSING DIRECTORY: $company_name"
        MISSING_DIR=$((MISSING_DIR + 1))
        continue
    fi
    
    company_info="$COMPANY_ANALYSIS_DIR/$company_name/company-info.md"
    company_people="$COMPANY_ANALYSIS_DIR/$company_name/company-people.json"
    
    if [ ! -f "$company_info" ] || [ ! -f "$company_people" ]; then
        echo "❌ MISSING FILES: $company_name"
        MISSING_FILES=$((MISSING_FILES + 1))
        NEED_PROCESSING=$((NEED_PROCESSING + 1))
        continue
    fi
    
    # Check if Company Mentions section exists
    if ! grep -q "## Company Mentions" "$company_info"; then
        echo "⚠️  MISSING MENTIONS: $company_name"
        MISSING_MENTIONS=$((MISSING_MENTIONS + 1))
        NEED_PROCESSING=$((NEED_PROCESSING + 1))
    else
        echo "✅ COMPLETE: $company_name"
        ALREADY_DONE=$((ALREADY_DONE + 1))
    fi
    
done < "$COMpanies_TO_PROCESS"

echo ""
echo "================================================"
echo "SUMMARY:"
echo "✅ Already completed: $ALREADY_DONE"
echo "⚠️  Need processing: $NEED_PROCESSING"
echo "   - Missing directory: $MISSING_DIR"
echo "   - Missing files: $MISSING_FILES" 
echo "   - Missing mentions: $MISSING_MENTIONS"
echo ""
echo "Companies that actually need processing:"
echo "================================================"

# Now show companies that need processing
while IFS= read -r company_path; do
    company_name=$(echo "$company_path" | sed 's|company_analysis/||')
    
    if [ ! -d "$COMPANY_ANALYSIS_DIR/$company_name" ]; then
        continue
    fi
    
    company_info="$COMPANY_ANALYSIS_DIR/$company_name/company-info.md"
    company_people="$COMPANY_ANALYSIS_DIR/$company_name/company-people.json"
    
    if [ ! -f "$company_info" ] || [ ! -f "$company_people" ] || ! grep -q "## Company Mentions" "$company_info"; then
        echo "$company_name"
    fi
    
done < "$COMpanies_TO_PROCESS" | head -20