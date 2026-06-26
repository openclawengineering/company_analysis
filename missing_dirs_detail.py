#!/usr/bin/env python3
import csv
import os

def main():
    missing_serials = [25, 166, 167, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 193, 194, 197, 199, 200, 202, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 267]
    
    master_companies = {}
    with open('master_gist.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['SerialNo'] and row['SerialNo'] != 'SerialNo':
                try:
                    master_companies[int(row['SerialNo'])] = row
                except ValueError:
                    continue
    
    print(f"Missing companies ({len(missing_serials)}):")
    print("-" * 80)
    for serial in missing_serials:
        if serial in master_companies:
            row = master_companies[serial]
            print(f"{serial}. {row['CompanyName']} | {row['Website']} | {row['Address']}")
        else:
            print(f"{serial}. NOT FOUND IN MASTER LIST")
    
    # Also check if any master list companies have dirs with different naming
    company_analysis_dir = '/home/openclaw_user/.openclaw/workspace/company_analysis'
    existing_dirs = {}
    for item in os.listdir(company_analysis_dir):
        if os.path.isdir(os.path.join(company_analysis_dir, item)):
            if '_' in item:
                try:
                    num = int(item.split('_')[0])
                    existing_dirs[num] = item
                except ValueError:
                    continue
    
    # Check for naming mismatches
    print("\n\nNaming mismatches (in master but dir has different name):")
    for serial in missing_serials:
        if serial not in existing_dirs:
            # Check if there's a dir with a similar number but different name
            pass  # already handled above

if __name__ == "__main__":
    main()
