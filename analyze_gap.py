#!/usr/bin/env python3
import csv
import json
import os
import re

# Read the master gist CSV
csv_path = "/home/openclaw_user/.openclaw/workspace/master_gist.csv"

companies_from_gist = {}
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        serial = row['SerialNo']
        companies_from_gist[serial] = {
            'name': row['CompanyName'],
            'website': row['Website']
        }

print(f"Total companies in master gist: {len(companies_from_gist)}")

# Get all directories in the repo
repo_path = "/home/openclaw_user/.openclaw/workspace/company_analysis"
existing_dirs = set()

for item in os.listdir(repo_path):
    if item.startswith('.') or item == '.git':
        continue
    item_path = os.path.join(repo_path, item)
    if os.path.isdir(item_path):
        existing_dirs.add(item)

# Check for companies that need work
companies_missing_directory = []
companies_null_social_profiles = []
companies_missing_mentions = []

for serial, company_data in sorted(companies_from_gist.items(), key=lambda x: int(x[0])):
    # Find matching directory
    matching_dirs = [d for d in existing_dirs if d.startswith(f"{serial}_")]

    if not matching_dirs:
        companies_missing_directory.append((serial, company_data['name']))
        continue

    # Use the first matching directory
    dir_name = matching_dirs[0]
    dir_path = os.path.join(repo_path, dir_name)

    # Check for company-info.md
    info_path = os.path.join(dir_path, "company-info.md")
    if not os.path.exists(info_path):
        companies_missing_mentions.append((serial, dir_name))
        continue

    # Check for Company Mentions section
    with open(info_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if '## Company Mentions' not in content and '## 企業の言及' not in content and '## 企業の言及' not in content:
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
    except Exception as e:
        companies_null_social_profiles.append((serial, dir_name))

print(f"\n=== GAP ANALYSIS ===")
print(f"Companies with no directory in repo: {len(companies_missing_directory)}")
for serial, name in companies_missing_directory[:10]:
    print(f"  - {serial}: {name}")

print(f"\nCompanies with all-null social profiles: {len(companies_null_social_profiles)}")
for serial, name in companies_null_social_profiles[:10]:
    print(f"  - {serial}: {name}")

print(f"\nCompanies missing Company Mentions: {len(companies_missing_mentions)}")
for serial, name in companies_missing_mentions[:10]:
    print(f"  - {serial}: {name}")

# Calculate unique companies needing work
all_needing_work_serials = set()
all_needing_work_serials.update([s for s, _ in companies_missing_directory])
all_needing_work_serials.update([s for s, _ in companies_null_social_profiles])
all_needing_work_serials.update([s for s, _ in companies_missing_mentions])

print(f"\n=== SUMMARY ===")
print(f"Unique companies needing work: {len(all_needing_work_serials)}")
print(f"Companies from gist: {len(companies_from_gist)}")
print(f"Percentage complete: {((len(companies_from_gist) - len(all_needing_work_serials)) / len(companies_from_gist) * 100):.1f}%")

# Save list of companies to work on
with open('/home/openclaw_user/.openclaw/workspace/companies_to_work.txt', 'w') as f:
    for serial in sorted(all_needing_work_serials, key=lambda x: int(x)):
        if serial in companies_from_gist:
            f.write(f"{serial}\n")

print(f"\nList of companies to work on saved to: companies_to_work.txt")