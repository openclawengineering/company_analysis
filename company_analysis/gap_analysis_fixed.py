#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

def check_company_gap():
    """Check companies 1-76 for missing data"""
    
    # Companies 1-76 from the master gist
    master_companies = set(range(1, 77))
    
    # Check current directories
    current_dirs = []
    for item in os.listdir('.'):
        # Extract number from directory name (any company 1-76)
        match = re.match(r'^(\d+)_', item)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 76:
                current_dirs.append(num)
    
    current_companies = set(current_dirs)
    
    # Check for companies with all-null social profiles and missing Company Mentions
    null_social_companies = []
    missing_mentions_companies = []
    
    for company_num in sorted(master_companies):
        dir_name = None
        # Find the directory for this company number
        for item in os.listdir('.'):
            match = re.match(r'^' + str(company_num) + r'_(.*)', item)
            if match:
                dir_name = item
                break
        
        if not dir_name:
            continue
            
        company_path = Path(dir_name)
        
        # Check company-people.json for all-null social profiles
        people_json_path = company_path / 'company-people.json'
        if people_json_path.exists():
            try:
                with open(people_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Check if social_profiles is empty or all profiles have null LinkedIn and Twitter
                if not data.get('social_profiles'):
                    null_social_companies.append(company_num)
                else:
                    all_null = True
                    for profile in data['social_profiles']:
                        if profile.get('linkedin') or profile.get('twitter'):
                            all_null = False
                            break
                    if all_null:
                        null_social_companies.append(company_num)
                        
            except (json.JSONDecodeError, FileNotFoundError):
                null_social_companies.append(company_num)
        
        # Check company-info.md for missing Company Mentions section
        info_md_path = company_path / 'company-info.md'
        if info_md_path.exists():
            try:
                with open(info_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if '## Company Mentions' not in content:
                    missing_mentions_companies.append(company_num)
                    
            except FileNotFoundError:
                missing_mentions_companies.append(company_num)
    
    # Calculate gap
    gap_count = len(null_social_companies) + len(missing_mentions_companies)
    
    # Print results
    print("=== Gap Analysis Results ===")
    print(f"Companies from master gist (1-76): {len(master_companies)}")
    print(f"Companies with directories in repo: {len(current_companies)}")
    print(f"Companies with all-null social profiles: {len(null_social_companies)}")
    print(f"Companies missing Company Mentions: {len(missing_mentions_companies)}")
    print(f"Total gap count: {gap_count}")
    
    if gap_count > 0:
        print("\n=== Companies needing social profile research ===")
        for num in null_social_companies:
            print(f"  Company {num}")
        
        print("\n=== Companies needing Company Mentions ===")
        for num in missing_mentions_companies:
            print(f"  Company {num}")
    
    return {
        'total_gap': gap_count,
        'null_social_companies': null_social_companies,
        'missing_mentions_companies': missing_mentions_companies,
        'current_companies': current_companies
    }

if __name__ == "__main__":
    result = check_company_gap()