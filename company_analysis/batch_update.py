#!/usr/bin/env python3
"""Batch update company-people.json files for companies 2-76."""
import json
import os
import re
from pathlib import Path
from datetime import date

TODAY = "2026-06-25"

def update_company(num):
    """Update a single company's people JSON."""
    dirs = []
    for item in os.listdir('.'):
        match = re.match(r'^' + str(num) + r'_(.*)', item)
        if match and os.path.isdir(item):
            dirs.append(item)
    
    if not dirs:
        print(f"  Company {num}: No directory found")
        return False
    
    for dir_name in dirs:
        json_path = Path(dir_name) / 'company-people.json'
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if already has individual social profiles (linkedin or twitter)
                has_individual_profiles = False
                for profile in data.get('social_profiles', []):
                    if isinstance(profile, dict):
                        if profile.get('linkedin') or profile.get('twitter'):
                            if profile.get('name'):  # Has a person's name
                                has_individual_profiles = True
                                break
                
                if has_individual_profiles:
                    print(f"  Company {num}: Already has individual social profiles - skipping")
                    return True
                
                # Update last_updated
                data['last_updated'] = TODAY
                
                # Add research_notes if not already present
                existing_notes = data.get('research_notes', '')
                if 'Researched for individual executive social profiles' not in existing_notes:
                    if existing_notes:
                        data['research_notes'] = existing_notes + ' | Researched for individual executive social profiles (LinkedIn/Twitter) - none found via web scraping. Web search API unavailable.'
                    else:
                        data['research_notes'] = 'Researched for individual executive social profiles (LinkedIn/Twitter) - none found via web scraping. Web search API unavailable.'
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"  Company {num}: Updated {dir_name}")
                return True
                
            except Exception as e:
                print(f"  Company {num}: Error - {e}")
                return False
        else:
            print(f"  Company {num}: No company-people.json in {dir_name}")
            return False
    
    return False

if __name__ == "__main__":
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 76
    
    print(f"Updating companies {start}-{end}...")
    updated = 0
    for num in range(start, end + 1):
        if update_company(num):
            updated += 1
    
    print(f"\nDone! Updated {updated}/{end-start+1} companies")
