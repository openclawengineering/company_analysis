#!/usr/bin/env python3
"""
Validate company-data.json against the expected schema.
Usage: python3 validate_json.py [--quiet]
"""

import json
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "company-data.json")

REQUIRED_TOP_LEVEL = {
    "company_folder_name": str,
    "company_name_en": (str, type(None)),
    "company_name_jp": (str, type(None)),
    "company_domains": list,
    "products_and_services": list,
    "company_profile": dict,
    "people": list,
    "partners": list,
    "certifications": list,
    "links": list,
    "tech_stack": list,
}

REQUIRED_PROFILE = {
    "address": (str, type(None)),
    "phone": (str, type(None)),
    "fax": (str, type(None)),
    "founded": (str, type(None)),
    "established": (str, type(None)),
    "capital": (str, type(None)),
    "num_of_employees": (str, type(None)),
    "sales": list,
}

REQUIRED_PERSON = {
    "name_en": (str, type(None)),
    "name_jp": (str, type(None)),
    "title": (str, type(None)),
    "notes": (str, type(None)),
    "linkedin": dict,
    "twitter": dict,
}

REQUIRED_LINK = {
    "name_and_description": (str, type(None)),
    "url": (str, type(None)),
}

REQUIRED_PRODUCT = {
    "name": (str, type(None)),
    "type": (str, type(None)),
    "client_type": (str, type(None)),
    "description": (str, type(None)),
    "target_demography": (str, type(None)),
}


def check_type(value, expected):
    if isinstance(expected, tuple):
        return isinstance(value, expected)
    return isinstance(value, expected)


def validate(data):
    errors = []
    warnings = []

    if not isinstance(data, list):
        errors.append("Root must be a JSON array")
        return errors, warnings

    for i, company in enumerate(data):
        folder = company.get("company_folder_name", f"<entry {i}>")
        prefix = f"[{i}] {folder}"

        # Check required top-level fields
        for field, expected_type in REQUIRED_TOP_LEVEL.items():
            if field not in company:
                errors.append(f"{prefix}: missing required field '{field}'")
            elif not check_type(company[field], expected_type):
                actual = type(company[field]).__name__
                if isinstance(expected_type, tuple):
                    expected_names = "/".join(t.__name__ for t in expected_type)
                else:
                    expected_names = expected_type.__name__
                errors.append(f"{prefix}: field '{field}' expected {expected_names}, got {actual}")

        # Check company_profile sub-fields
        profile = company.get("company_profile")
        if isinstance(profile, dict):
            for field, expected_type in REQUIRED_PROFILE.items():
                if field not in profile:
                    errors.append(f"{prefix}/company_profile: missing field '{field}'")
                elif not check_type(profile[field], expected_type):
                    actual = type(profile[field]).__name__
                    if isinstance(expected_type, tuple):
                        expected_names = "/".join(t.__name__ for t in expected_type)
                    else:
                        expected_names = expected_type.__name__
                    errors.append(f"{prefix}/company_profile: '{field}' expected {expected_names}, got {actual}")

            # Check sales entries
            for j, sale in enumerate(profile.get("sales", [])):
                if not isinstance(sale, dict):
                    errors.append(f"{prefix}/company_profile/sales[{j}]: expected dict, got {type(sale).__name__}")
                else:
                    for sf in ["date_type", "date", "total_sales"]:
                        if sf not in sale:
                            warnings.append(f"{prefix}/company_profile/sales[{j}]: missing '{sf}'")
        elif profile is not None:
            errors.append(f"{prefix}: 'company_profile' expected dict, got {type(profile).__name__}")

        # Check people entries
        for j, person in enumerate(company.get("people", [])):
            if not isinstance(person, dict):
                errors.append(f"{prefix}/people[{j}]: expected dict, got {type(person).__name__}")
                continue
            for field, expected_type in REQUIRED_PERSON.items():
                if field not in person:
                    errors.append(f"{prefix}/people[{j}] ({person.get('name_jp', '?')}): missing '{field}'")
                elif not check_type(person[field], expected_type):
                    actual = type(person[field]).__name__
                    errors.append(f"{prefix}/people[{j}]: '{field}' type mismatch")

            # Check linkedin/twitter sub-objects
            for social_key in ["linkedin", "twitter"]:
                social = person.get(social_key)
                if isinstance(social, dict):
                    for sf in ["profile_available", "data_available", "url"]:
                        if sf not in social:
                            warnings.append(f"{prefix}/people[{j}]/{social_key}: missing '{sf}'")

        # Check links entries
        for j, link in enumerate(company.get("links", [])):
            if not isinstance(link, dict):
                errors.append(f"{prefix}/links[{j}]: expected dict, got {type(link).__name__}")
                continue
            for field, expected_type in REQUIRED_LINK.items():
                if field not in link:
                    warnings.append(f"{prefix}/links[{j}]: missing '{field}'")

        # Check products_and_services entries
        for j, prod in enumerate(company.get("products_and_services", [])):
            if not isinstance(prod, dict):
                errors.append(f"{prefix}/products_and_services[{j}]: expected dict, got {type(prod).__name__}")
                continue
            for field, expected_type in REQUIRED_PRODUCT.items():
                if field not in prod:
                    warnings.append(f"{prefix}/products_and_services[{j}]: missing '{field}'")

        # Check list fields contain correct types
        for list_field, item_type in [("company_domains", str), ("partners", str),
                                       ("certifications", str), ("tech_stack", str)]:
            items = company.get(list_field, [])
            for j, item in enumerate(items):
                if not isinstance(item, item_type) and item is not None:
                    errors.append(f"{prefix}/{list_field}[{j}]: expected str, got {type(item).__name__}")

    return errors, warnings


def main():
    quiet = "--quiet" in sys.argv

    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found")
        sys.exit(1)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON - {e}")
        sys.exit(1)

    errors, warnings = validate(data)

    if not quiet:
        print(f"Validating {len(data)} companies...")
        print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")

    if warnings and not quiet:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    if not errors:
        print(f"\nVALID: {len(data)} companies pass validation.")
        if warnings:
            print(f"  ({len(warnings)} warnings)")
        sys.exit(0)
    else:
        print(f"\nINVALID: {len(errors)} errors found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
