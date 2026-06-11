#!/usr/bin/env python3
"""
CLI tool for CRUD operations on company data using company_folder_name as lookup key.

Usage:
    python company_tool.py read --name "folder_name"
    python company_tool.py verify --name "folder_name" [--field company_domains]
    python company_tool.py update --name "folder_name" --field company_name_en --value "New Name"
    python company_tool.py delete --name "folder_name"
    python company_tool.py list [--domain "System Development"]
"""

import argparse
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "company-data.json")


# ---------------------------------------------------------------------------
# Core Data Layer
# ---------------------------------------------------------------------------

def load_data():
    """Load company-data.json and return the parsed JSON list."""
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_index(data):
    """Build a dict mapping company_folder_name -> list index for O(1) lookup."""
    return {entry["company_folder_name"]: i for i, entry in enumerate(data)}


def save_data(data):
    """Write the full JSON list back to company-data.json with proper formatting."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def find_company(data, index, name, exact_only=False):
    """Find company by folder name. Returns (match_type, results).

    match_type: "exact", "partial", or "none"
    results: list of (folder_name, entry) tuples
    """
    if name in index:
        entry = data[index[name]]
        return "exact", [(name, entry)]

    if exact_only:
        # For update/delete, find partial matches to suggest to user
        partials = [
            (entry["company_folder_name"], entry)
            for entry in data
            if name in entry["company_folder_name"]
        ]
        if partials:
            return "partial", partials
        return "none", []

    # Partial matching for read/verify
    partials = [
        (entry["company_folder_name"], entry)
        for entry in data
        if name in entry["company_folder_name"]
    ]
    if partials:
        return "partial", partials

    return "none", []


def get_nested_field(entry, field_path):
    """Get a nested field value using dot-path notation (e.g., 'company_profile.address')."""
    parts = field_path.split(".")
    current = entry
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None, False  # field not found
    return current, True


def set_nested_field(entry, field_path, value):
    """Set a nested field value using dot-path notation. Returns True on success."""
    parts = field_path.split(".")
    current = entry
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    last_key = parts[-1]
    if isinstance(current, dict) and last_key in current:
        current[last_key] = value
        return True
    return False


# ---------------------------------------------------------------------------
# Read Command
# ---------------------------------------------------------------------------

def cmd_read(args, data, index):
    name = args.name
    match_type, results = find_company(data, index, name)

    if match_type == "none":
        print(f"No company found matching '{name}'")
        sys.exit(1)

    if match_type == "exact":
        _, entry = results[0]
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return

    # Partial match
    print(f"No exact match for '{name}'. Partial matches:")
    for folder_name, entry in results:
        print(f"  {folder_name}  ({entry.get('company_name_en', 'N/A')})")


# ---------------------------------------------------------------------------
# Verify Command
# ---------------------------------------------------------------------------

def _get_company_folder_path(folder_name):
    """Return the filesystem path for a company folder."""
    return os.path.join(ROOT_DIR, folder_name)


def verify_domains(entry, folder_path):
    """Verify company_domains against company-info.md Business Fields."""
    info_file = os.path.join(folder_path, "company-info.md")
    if not os.path.exists(info_file):
        return ["SKIP: company-info.md not found in folder"]

    with open(info_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Business Fields line
    business_fields = ""
    for line in content.split("\n"):
        if "Business Fields" in line:
            business_fields = line.split(":", 1)[-1].strip()
            break

    json_domains = set(entry.get("company_domains", []))
    issues = []

    if not json_domains and not business_fields:
        issues.append("OK: Both empty")
    elif not json_domains and business_fields:
        issues.append(f"MISMATCH: JSON has no domains, but source has: {business_fields}")
    elif json_domains and not business_fields:
        issues.append(f"MISMATCH: JSON has domains {json_domains}, but source has no Business Fields")
    else:
        issues.append(f"JSON domains: {sorted(json_domains)}")
        issues.append(f"Source Business Fields: {business_fields}")
        issues.append("NOTE: Manual comparison needed (source uses Japanese domain names)")

    return issues


def verify_profile(entry, folder_path):
    """Verify company_profile fields against company-info.md."""
    info_file = os.path.join(folder_path, "company-info.md")
    if not os.path.exists(info_file):
        return ["SKIP: company-info.md not found in folder"]

    with open(info_file, "r", encoding="utf-8") as f:
        content = f.read()

    profile = entry.get("company_profile", {})
    issues = []

    field_map = {
        "address": "Address",
        "phone": "Phone",
        "fax": "Fax",
    }

    for json_key, md_label in field_map.items():
        json_val = profile.get(json_key)
        # Extract from markdown
        md_val = None
        for line in content.split("\n"):
            if f"**{md_label}**" in line:
                md_val = line.split(":", 1)[-1].strip() if ":" in line else None
                break

        if json_val and md_val and json_val != md_val:
            issues.append(f"MISMATCH {json_key}: JSON='{json_val}' vs Source='{md_val}'")
        elif not json_val and md_val:
            issues.append(f"MISSING in JSON {json_key}: Source has '{md_val}'")
        elif json_val and not md_val:
            issues.append(f"OK {json_key}: JSON has value, not found in source")

    return issues if issues else ["OK: Profile fields match (or both empty)"]


def verify_people(entry, folder_path):
    """Verify people entries against company-people.json."""
    people_file = os.path.join(folder_path, "company-people.json")
    if not os.path.exists(people_file):
        return ["SKIP: company-people.json not found in folder"]

    with open(people_file, "r", encoding="utf-8") as f:
        source = json.load(f)

    source_people = source.get("people", [])
    json_people = entry.get("people", [])

    issues = []

    if len(source_people) != len(json_people):
        issues.append(f"COUNT MISMATCH: Source has {len(source_people)} people, JSON has {len(json_people)}")

    source_names = {p.get("name", "") for p in source_people}
    json_names = {p.get("name_en", "") or p.get("name_jp", "") for p in json_people}

    for name in source_names - json_names:
        if name:
            issues.append(f"In SOURCE but not JSON: {name}")
    for name in json_names - source_names:
        if name:
            issues.append(f"In JSON but not SOURCE: {name}")

    return issues if issues else ["OK: People entries match"]


def cmd_verify(args, data, index):
    name = args.name
    match_type, results = find_company(data, index, name)

    if match_type == "none":
        print(f"No company found matching '{name}'")
        sys.exit(1)

    if match_type == "partial":
        print(f"No exact match for '{name}'. Partial matches:")
        for folder_name, entry in results:
            print(f"  {folder_name}  ({entry.get('company_name_en', 'N/A')})")
        return

    folder_name, entry = results[0]
    folder_path = _get_company_folder_path(folder_name)

    if not os.path.isdir(folder_path):
        print(f"WARNING: Company folder not found on disk: {folder_path}")
        print("Cannot verify - source folder is missing.")
        return

    field = args.field
    verifiers = {
        "company_domains": verify_domains,
        "company_profile": verify_profile,
        "people": verify_people,
    }

    if field:
        if field not in verifiers:
            print(f"Unknown field '{field}'. Supported: {', '.join(verifiers.keys())}")
            sys.exit(1)
        print(f"\n=== Verifying {field} for {folder_name} ===")
        issues = verifiers[field](entry, folder_path)
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n=== Verifying ALL fields for {folder_name} ===")
        for field_name, verifier in verifiers.items():
            print(f"\n--- {field_name} ---")
            issues = verifier(entry, folder_path)
            for issue in issues:
                print(f"  {issue}")


# ---------------------------------------------------------------------------
# Update Command
# ---------------------------------------------------------------------------

def cmd_update(args, data, index):
    name = args.name
    match_type, results = find_company(data, index, name, exact_only=True)

    if match_type == "partial":
        print(f"Ambiguous match for '{name}'. Please use an exact company_folder_name:")
        for folder_name, entry in results:
            print(f"  {folder_name}")
        sys.exit(1)

    if match_type == "none":
        print(f"No company found matching '{name}'")
        sys.exit(1)

    folder_name, entry = results[0]
    field = args.field

    # Get the value
    if args.value_from_file:
        with open(args.value_from_file, "r", encoding="utf-8") as f:
            value = json.load(f)
    else:
        value = args.value

    # Handle append for list fields
    if args.append:
        current, found = get_nested_field(entry, field)
        if not found:
            print(f"Error: Field '{field}' does not exist.", file=sys.stderr)
            sys.exit(1)
        if not isinstance(current, list):
            print(f"Error: Cannot append to non-list field '{field}'.", file=sys.stderr)
            sys.exit(1)
        if value in current:
            print(f"Value '{value}' already exists in {field}.")
            return
        current.append(value)
        value = current  # for the confirmation message
    else:
        # Validate field path exists
        _, found = get_nested_field(entry, field)
        if not found:
            print(f"Error: Field path '{field}' does not exist.", file=sys.stderr)
            sys.exit(1)
        if not set_nested_field(entry, field, value):
            print(f"Error: Failed to set field '{field}'.", file=sys.stderr)
            sys.exit(1)

    save_data(data)
    print(f"Updated {field} = {value!r} for {folder_name}")


# ---------------------------------------------------------------------------
# Delete Command
# ---------------------------------------------------------------------------

def cmd_delete(args, data, index):
    name = args.name
    match_type, results = find_company(data, index, name, exact_only=True)

    if match_type == "partial":
        print(f"Ambiguous match for '{name}'. Please use an exact company_folder_name:")
        for folder_name, _ in results:
            print(f"  {folder_name}")
        sys.exit(1)

    if match_type == "none":
        print(f"No company found matching '{name}'")
        sys.exit(1)

    folder_name, _ = results[0]
    confirm = input(f"Are you sure you want to delete '{folder_name}'? (y/N): ").strip().lower()

    if confirm != "y":
        print("Delete cancelled.")
        return

    idx = index[folder_name]
    del data[idx]
    save_data(data)
    print(f"Deleted '{folder_name}' from company-data.json")


# ---------------------------------------------------------------------------
# List Command
# ---------------------------------------------------------------------------

def cmd_list(args, data, _index):
    domain_filter = args.domain

    if domain_filter:
        matches = [
            entry["company_folder_name"]
            for entry in data
            if domain_filter in entry.get("company_domains", [])
        ]
        if not matches:
            print(f"No companies found with domain '{domain_filter}'")
            return
        matches.sort()
        for name in matches:
            print(name)
    else:
        names = sorted(entry["company_folder_name"] for entry in data)
        for name in names:
            print(name)


# ---------------------------------------------------------------------------
# CLI Setup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CRUD tool for company data using company_folder_name as lookup key."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # read
    read_parser = subparsers.add_parser("read", help="Read a company entry")
    read_parser.add_argument("--name", required=True, help="Company folder name (supports partial matching)")

    # verify
    verify_parser = subparsers.add_parser("verify", help="Verify company fields against source files")
    verify_parser.add_argument("--name", required=True, help="Company folder name (supports partial matching)")
    verify_parser.add_argument("--field", default=None, help="Specific field to verify (company_domains, company_profile, people)")

    # update
    update_parser = subparsers.add_parser("update", help="Update a company entry field")
    update_parser.add_argument("--name", required=True, help="Exact company folder name")
    update_parser.add_argument("--field", required=True, help="Field to update (supports dot-path notation)")
    update_parser.add_argument("--value", default=None, help="New value for the field")
    update_parser.add_argument("--append", action="store_true", help="Append value to a list field")
    update_parser.add_argument("--value-from-file", default=None, help="Read value from a JSON file")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a company entry")
    delete_parser.add_argument("--name", required=True, help="Exact company folder name")

    # list
    list_parser = subparsers.add_parser("list", help="List company folder names")
    list_parser.add_argument("--domain", default=None, help="Filter by company domain")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_data()
    index = build_index(data)

    if args.command == "read":
        cmd_read(args, data, index)
    elif args.command == "verify":
        cmd_verify(args, data, index)
    elif args.command == "update":
        cmd_update(args, data, index)
    elif args.command == "delete":
        cmd_delete(args, data, index)
    elif args.command == "list":
        cmd_list(args, data, index)


if __name__ == "__main__":
    main()
