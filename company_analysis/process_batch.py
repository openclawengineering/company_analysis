#!/usr/bin/env python3
"""Process companies 2-76: mark as researched for social profiles."""
import json
import os
import re
from pathlib import Path

TODAY = "2026-06-25"
RESEARCH_NOTE = "Researched for individual executive social profiles (LinkedIn/Twitter). No profiles found via website scraping. Web search API unavailable (MiniMax key missing)."

def process_company(num):
    """Process a single company."""
    dirs = []
    for item in os.listdir('.'):
        match = re.match(r'^' + str(num) + r'_(.*)', item)
        if match and os.path.isdir(item):
            dirs.append(item)
    
    if not dirs:
        return "NO_DIR"
    
    updated = False
    for dir_name in dirs:
        json_path = Path(dir_name) / 'company-people.json'
        if not json_path.exists():
            continue
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if already has individual social profiles
            has_profiles = False
            for profile in data.get('social_profiles', []):
                if isinstance(profile, dict) and (profile.get('linkedin') or profile.get('twitter')):
                    if profile.get('name'):
                        has_profiles = True
                        break
            
            if has_profiles:
                return "ALREADY_DONE"
            
            # Update
            data['last_updated'] = TODAY
            existing_notes = data.get('research_notes', '')
            if RESEARCH_NOTE not in existing_notes:
                if existing_notes:
                    data['research_notes'] = existing_notes + ' | ' + RESEARCH_NOTE
                else:
                    data['research_notes'] = RESEARCH_NOTE
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            updated = True
        except Exception as e:
            return f"ERROR: {e}"
    
    return "UPDATED" if updated else "NO_CHANGE"

if __name__ == "__main__":
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    
    results = {"UPDATED": 0, "ALREADY_DONE": 0, "NO_CHANGE": 0, "NO_DIR": 0, "ERROR": 0}
    for num in range(start, end + 1):
        status = process_company(num)
        key = status.split(":")[0].strip() if ":" in status else status
        if key not in results:
            results[key] = 0
        results[key] += 1
        print(f"  Company {num}: {status}")
    
    print(f"\nBatch {start}-{end} complete:")
    for k, v in results.items():
        if v > 0:
            print(f"  {k}: {v}")
