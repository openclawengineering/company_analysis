#!/usr/bin/env python3
import json
import os
import re
import csv
from pathlib import Path

def get_social_profiles_null_count(company_people_path):
    """Check if a company-people.json has all-null social profiles"""
    try:
        with open(company_people_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'social_profiles' in data and data['social_profiles']:
            all_null = True
            for profile in data['social_profiles']:
                if profile.get('linkedin') or profile.get('twitter'):
                    all_null = False
                    break
            return 1 if all_null else 0
        return 1  # No social profiles = needs work
    except (json.JSONDecodeError, FileNotFoundError):
        return 1  # File missing or invalid = needs work

def get_mentions_missing(company_info_path):
    """Check if a company-info.md is missing Company Mentions section"""
    try:
        with open(company_info_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Company Mentions section
        return 1 if '## Company Mentions' not in content else 0
    except FileNotFoundError:
        return 1  # File missing = needs work

def main():
    # Read master gist CSV
    master_companies = {}
    with open('master_gist.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['SerialNo'] and row['SerialNo'] != 'SerialNo':
                try:
                    master_companies[int(row['SerialNo'])] = row
                except ValueError:
                    continue

    companies_to_work = []
    company_analysis_dir = Path('/home/openclaw_user/.openclaw/workspace/company_analysis')

    for serial_num in sorted(master_companies.keys()):
        company_name = master_companies[serial_num]['CompanyName']
        company_dir = company_analysis_dir / f"{serial_num}_{company_name}"
        
        if not company_dir.exists():
            print(f"Directory missing for company {serial_num}: {company_name}")
            companies_to_work.append({
                'serial': serial_num,
                'name': company_name,
                'reason': ['missing_directory']
            })
            continue

        # Check company-people.json
        people_file = company_dir / 'company-people.json'
        needs_people_work = get_social_profiles_null_count(people_file)
        
        # Check company-info.md  
        info_file = company_dir / 'company-info.md'
        needs_mentions_work = get_mentions_missing(info_file)
        
        if needs_people_work or needs_mentions_work:
            reason = []
            if needs_people_work:
                reason.append("social_profiles_null")
            if needs_mentions_work:
                reason.append("missing_mentions")
            
            companies_to_work.append({
                'serial': serial_num,
                'name': company_name,
                'reason': reason
            })

    print(f"Total companies needing work: {len(companies_to_work)}")
    
    if companies_to_work:
        print(f"\nFirst 10 companies needing work:")
        for i, company in enumerate(companies_to_work[:10]):
            print(f"{i+1}. {company['serial']}: {company['name']} ({', '.join(company['reason'])})")
        
        # Save to file
        with open('companies_to_work.txt', 'w') as f:
            for company in companies_to_work:
                f.write(f"{company['serial']}_{company['name']}\n")
        
        print(f"\nCompanies to work saved to companies_to_work.txt")
    else:
        print("All companies are complete!")

if __name__ == "__main__":
    main()