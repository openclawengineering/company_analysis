## Why

Performing operations on a specific company (e.g., verifying domains, updating profile data, checking people entries) currently requires scanning the entire `company-data.json` (306 entries) or manually navigating the filesystem. There is no tool to quickly look up, validate, or modify a company's data using its `company_folder_name` as the primary key. This slows down batch operations and makes targeted data quality work tedious.

## What Changes

- Add a Python CLI tool (`company_tool.py`) that accepts a `company_folder_name` and a CRUD operation command
- Support **Read**: retrieve and display a company's full entry from `company-data.json` by folder name
- Support **Verify**: validate specific fields (e.g., `company_domains`, `company_profile`, `people`) against the source files in the company's physical folder
- Support **Update**: modify specific fields in a company's JSON entry (e.g., add a domain, update address, fix a name)
- Support **Delete**: remove a company entry from `company-data.json` by folder name
- Support **List**: show all `company_folder_name` values with optional domain-based filtering

## Capabilities

### New Capabilities
- `company-crud`: CLI tool for performing CRUD operations on company data entries using `company_folder_name` as the lookup key, including read, verify, update, delete, and list commands

### Modified Capabilities
<!-- No existing specs require requirement changes -->

## Impact

- **New file**: `company_tool.py` (Python CLI script in project root)
- **Reads from**: `company-data.json`, individual company folders
- **Writes to**: `company-data.json` (for update/delete operations)
- **Dependencies**: Python standard library only (json, argparse, os, pathlib)
