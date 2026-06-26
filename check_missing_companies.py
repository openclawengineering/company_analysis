#!/usr/bin/env python3
import csv
import os
import sys

def main():
    # Read master gist CSV
    master_companies = {}
    with open('master_gist.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip header row and empty rows
            if row['SerialNo'] and row['SerialNo'] != 'SerialNo':
                try:
                    master_companies[int(row['SerialNo'])] = row
                except ValueError:
                    continue
    
    # Get existing directories
    existing_dirs = set()
    company_analysis_dir = '/home/openclaw_user/.openclaw/workspace/company_analysis'
    
    for item in os.listdir(company_analysis_dir):
        if os.path.isdir(os.path.join(company_analysis_dir, item)):
            # Extract number from directory name like "1_アークシステム株式会社"
            if '_' in item:
                try:
                    num = int(item.split('_')[0])
                    existing_dirs.add(num)
                except ValueError:
                    continue
    
    # Find missing companies
    missing_companies = []
    for serial_num in sorted(master_companies.keys()):
        if serial_num not in existing_dirs:
            missing_companies.append(serial_num)
    
    print(f"Total companies in master list: {len(master_companies)}")
    print(f"Existing directories: {len(existing_dirs)}")
    print(f"Missing directories: {len(missing_companies)}")
    
    if missing_companies:
        print(f"\nMissing companies (first 10): {missing_companies[:10]}")
        print(f"Missing companies (last 10): {missing_companies[-10:]}")
        
        # Write missing companies to file
        with open('missing_companies.txt', 'w') as f:
            for num in missing_companies:
                f.write(f"{num}\n")
        
        print(f"\nMissing companies saved to missing_companies.txt")
    else:
        print("All companies have directories!")

if __name__ == "__main__":
    main()