#!/usr/bin/env python3
import csv
import json
import os
import re

# Read the master gist CSV
csv_url = "https://gist.githubusercontent.com/hazrat-arisaftech/2dc68f7845553be258733cafa2cff7db/raw"

companies_missing_directory = []
companies_null_social_profiles = []
companies_missing_mentions = []

# Get all directories in the repo
repo_path = "/home/openclaw_user/.openclaw/workspace/company_analysis"
existing_dirs = set()

for item in os.listdir(repo_path):
    if item.startswith('.') or item == '.git':
        continue
    item_path = os.path.join(repo_path, item)
    if os.path.isdir(item_path):
        existing_dirs.add(item)

# Since I can't download the CSV directly, I'll analyze existing directories
# and check for missing data

for dir_name in sorted(existing_dirs):
    if not re.match(r'^\d+_', dir_name):
        continue

    serial = dir_name.split('_')[0]
    dir_path = os.path.join(repo_path, dir_name)

    # Check for company-info.md
    info_path = os.path.join(dir_path, "company-info.md")
    if not os.path.exists(info_path):
        companies_missing_mentions.append((serial, dir_name))
        continue

    # Check for Company Mentions section
    with open(info_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if '## Company Mentions' not in content and '## 企業の言及' not in content:
            companies_missing_mentions.append((serial, dir_name))

    # Check for company-people.json
    people_path = os.path.join(dir_path, "company-people.json")
    if not os.path.exists(people_path):
        companies_null_social_profiles.append((serial, dir_name))
        continue

    # Check if social_profiles array has any non-null values
    try:
        with open(people_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        social_profiles = data.get('social_profiles', [])
        if not social_profiles or all(
            sp.get('linkedin') is None and sp.get('twitter') is None
            for sp in social_profiles
        ):
            companies_null_social_profiles.append((serial, dir_name))
    except:
        companies_null_social_profiles.append((serial, dir_name))

print(f"Companies with all-null social profiles: {len(companies_null_social_profiles)}")
for serial, name in companies_null_social_profiles[:10]:
    print(f"  - {serial}: {name}")

print(f"\nCompanies missing Company Mentions: {len(companies_missing_mentions)}")
for serial, name in companies_missing_mentions[:10]:
    print(f"  - {serial}: {name}")

print(f"\nTotal companies needing work: {len(set([x for x,_ in companies_null_social_profiles + companies_missing_mentions]))}")