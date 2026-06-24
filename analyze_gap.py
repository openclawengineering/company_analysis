#!/usr/bin/env python3
import csv
import os
import re

def get_master_companies():
    """Get all companies from master gist CSV"""
    companies = []
    with open('companies_from_gist.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append({
                'serial_no': int(row['SerialNo']),
                'name': row['CompanyName'],
                'website': row['Website']
            })
    return companies

def get_existing_directories():
    """Get list of existing directories in company_analysis"""
    directories = []
    company_analysis_dir = 'company_analysis'
    
    if os.path.exists(company_analysis_dir):
        for item in os.listdir(company_analysis_dir):
            if os.path.isdir(os.path.join(company_analysis_dir, item)):
                # Extract serial number from directory name
                match = re.match(r'^(\d+)_', item)
                if match:
                    serial_no = int(match.group(1))
                    directories.append(serial_no)
    
    return directories

def analyze_gap():
    print("Analyzing company research gap...")
    
    # Get all companies from master gist
    master_companies = get_master_companies()
    print(f"Total companies in master gist: {len(master_companies)}")
    
    # Get existing directories
    existing_dirs = get_existing_directories()
    print(f"Existing directories in company_analysis: {len(existing_dirs)}")
    
    # Find missing companies
    missing_companies = []
    for company in master_companies:
        if company['serial_no'] not in existing_dirs:
            missing_companies.append(company)
    
    print(f"Missing companies: {len(missing_companies)}")
    
    # Print missing companies
    for company in missing_companies[:20]:  # Show first 20
        print(f"  {company['serial_no']}: {company['name']} ({company['website']})")
    
    if len(missing_companies) > 20:
        print(f"  ... and {len(missing_companies) - 20} more")
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"Master companies: {len(master_companies)}")
    print(f"Existing directories: {len(existing_dirs)}")
    print(f"Missing directories: {len(missing_companies)}")
    print(f"Gap: {len(missing_companies)} companies need work")
    
    return missing_companies

if __name__ == "__main__":
    missing = analyze_gap()
    
    # Save missing companies to file
    with open('missing_companies.txt', 'w', encoding='utf-8') as f:
        for company in missing:
            f.write(f"{company['serial_no']}\n")