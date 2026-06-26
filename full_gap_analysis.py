#!/usr/bin/env python3
import csv
import os
import json
from pathlib import Path

def normalize(s):
    """Normalize Japanese company names for comparison."""
    # Remove spaces, fullwidth/halfwidth variations
    s = s.strip()
    s = s.replace(' ', '').replace('　', '')
    s = s.replace('（', '(').replace('）', ')')
    s = s.replace('・', '').replace('･', '')
    return s.lower()

def main():
    company_analysis_dir = Path('/home/openclaw_user/.openclaw/workspace/company_analysis')
    
    # Get all existing directories by serial number
    existing_dirs = {}
    for item in os.listdir(company_analysis_dir):
        if os.path.isdir(os.path.join(company_analysis_dir, item)) and item[0].isdigit():
            parts = item.split('_', 1)
            if len(parts) == 2:
                try:
                    serial = int(parts[0])
                    rest = parts[1]
                    existing_dirs[serial] = item
                except ValueError:
                    continue

    # Read master gist CSV
    master_companies = {}
    with open('master_gist.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['SerialNo'] and row['SerialNo'] != 'SerialNo':
                try:
                    serial = int(row['SerialNo'])
                    master_companies[serial] = row['CompanyName']
                except ValueError:
                    continue

    # Check for truly missing serial numbers
    missing_serials = []
    for serial in sorted(master_companies.keys()):
        if serial not in existing_dirs:
            missing_serials.append(serial)
    
    print(f"Total in master: {len(master_companies)}")
    print(f"Total existing dirs: {len(existing_dirs)}")
    print(f"Truly missing serials: {len(missing_serials)}")
    
    if missing_serials:
        print(f"\nMissing: {missing_serials}")
    
    # Now check what actually needs work among existing directories
    print("\n--- QUALITY CHECK ---")
    
    no_mentions = []
    all_null_social = []
    no_people_json = []
    no_info_md = []
    empty_dirs = []
    
    for serial in sorted(existing_dirs.keys()):
        dir_name = existing_dirs[serial]
        dir_path = company_analysis_dir / dir_name
        
        files = os.listdir(dir_path)
        
        # Check for empty dirs
        md_files = [f for f in files if f.endswith('.md')]
        json_files = [f for f in files if f.endswith('.json')]
        
        if not md_files and not json_files:
            empty_dirs.append((serial, dir_name))
            continue
        
        has_info = 'company-info.md' in files
        has_people = 'company-people.json' in files
        
        if not has_info:
            no_info_md.append((serial, dir_name))
            continue
        
        if not has_people:
            no_people_json.append((serial, dir_name))
            continue
        
        # Check mentions
        info_path = dir_path / 'company-info.md'
        with open(info_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '## Company Mentions' not in content:
            no_mentions.append((serial, dir_name))
        
        # Check social profiles
        people_path = dir_path / 'company-people.json'
        try:
            with open(people_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            sp = data.get('social_profiles', [])
            has_social = any(p.get('linkedin') or p.get('twitter') for p in sp) if sp else False
            if not has_social:
                all_null_social.append((serial, dir_name))
        except:
            all_null_social.append((serial, dir_name))
    
    print(f"Empty dirs: {len(empty_dirs)}")
    for s, d in empty_dirs[:5]:
        print(f"  {s}: {d}")
    
    print(f"No company-info.md: {len(no_info_md)}")
    for s, d in no_info_md[:5]:
        print(f"  {s}: {d}")
    
    print(f"No company-people.json: {len(no_people_json)}")
    for s, d in no_people_json[:5]:
        print(f"  {s}: {d}")
    
    print(f"Missing Company Mentions: {len(no_mentions)}")
    for s, d in no_mentions[:5]:
        print(f"  {s}: {d}")
    
    print(f"All-null social profiles: {len(all_null_social)}")
    for s, d in all_null_social[:5]:
        print(f"  {s}: {d}")

if __name__ == "__main__":
    main()
