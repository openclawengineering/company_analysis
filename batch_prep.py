#!/usr/bin/env python3
import csv
import json
import os
import re
from datetime import datetime

def process_company(serial, company_data, repo_path):
    """
    Process a single company: create directory structure, fetch data, and update files.
    """
    company_name = company_data['name']
    website = company_data['website']

    # Create directory name
    dir_name = f"{serial}_{company_name}"
    dir_path = os.path.join(repo_path, dir_name)

    # Create directory if it doesn't exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_name}")

    # Check existing files
    info_path = os.path.join(dir_path, "company-info.md")
    people_path = os.path.join(dir_path, "company-people.json")

    has_info = os.path.exists(info_path)
    has_people = os.path.exists(people_path)

    # Check if work is needed
    work_needed = False

    # Check for Company Mentions
    if has_info:
        with open(info_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if '## Company Mentions' not in content and '## 企業の言及' not in content:
                work_needed = True
                needs_mentions = True
            else:
                needs_mentions = False
    else:
        needs_mentions = True
        work_needed = True

    # Check for social profiles
    if has_people:
        try:
            with open(people_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            social_profiles = data.get('social_profiles', [])
            if not social_profiles or all(
                sp.get('linkedin') is None and sp.get('twitter') is None
                for sp in social_profiles
            ):
                work_needed = True
                needs_social = True
            else:
                needs_social = False
        except:
            needs_social = True
            work_needed = True
    else:
        needs_social = True
        work_needed = True

    return {
        'serial': serial,
        'name': company_name,
        'website': website,
        'dir_path': dir_path,
        'work_needed': work_needed,
        'needs_mentions': needs_mentions,
        'needs_social': needs_social,
        'has_info': has_info,
        'has_people': has_people
    }

# Read companies to work on
companies_to_process = []
with open('/home/openclaw_user/.openclaw/workspace/companies_to_work.txt', 'r') as f:
    serials = [line.strip() for line in f if line.strip()]

# Read master gist
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

repo_path = "/home/openclaw_user/.openclaw/workspace/company_analysis"

# Process first 10 companies
for serial in serials[:10]:
    if serial in companies_from_gist:
        result = process_company(serial, companies_from_gist[serial], repo_path)
        companies_to_process.append(result)
        print(f"Serial {serial}: {result['name']} - Work needed: {result['work_needed']}")