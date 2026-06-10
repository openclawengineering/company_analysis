## Why

Company data is scattered across 306 individual folders with mixed file formats (markdown, JSON). There is no consolidated, queryable data source. A single structured JSON file (`company-data.json`) is needed to aggregate all company information in a consistent schema for downstream analysis and reporting.

## What Changes

- Create a master `company-data.json` file containing structured data for all 306 companies
- Read and extract data from 4 file types per company folder:
  - `company-info.md` — company overview, address, phone, capital, founded date, business fields, services, partners, certifications, links, tech stack
  - `company-people.json` — people/key personnel with names, titles, notes
  - `social-profiles.md` — LinkedIn and Twitter profile URLs for people (165 folders)
  - `social-profile-scraped.json` — scraped LinkedIn/Twitter data including profile details (165 folders)
- Infer `company_domains` from business descriptions and services (e.g., "SES" → "Staffing/SES", "受託開発" → "Custom Software Development")
- Normalize domain names so the same domain always uses the same string
- Track progress against a checklist of all 306 companies
- Validate JSON structure every 5 companies using a validation script
- Missing/unavailable data fields should be set to `null`

## Capabilities

### New Capabilities
- `data-extraction`: Read company source files (md, json), parse/extract structured data, and map to the target JSON schema defined in `json-structure.md`
- `domain-normalization`: Normalize company domain names to a consistent taxonomy based on business descriptions and services
- `json-validation`: Script to validate `company-data.json` against the expected structure, checking for required fields, correct types, and valid format
- `progress-tracking`: Checklist of all 306 companies with completion status to track extraction progress

### Modified Capabilities
_(none — this is a greenfield effort)_

## Impact

- **Output file**: `company-data.json` will be created/populated at project root
- **Validation script**: New Python script for JSON format validation
- **No existing code broken**: This is a data extraction task, not a code modification
- **Dependencies**: Python 3 (already in use), standard library (`json`, `os`, `glob`)
