## Why

The `companies/` directory contains 306 company folders with unstructured and semi-structured data (markdown info files, JSON people data, social profiles), but there is no unified, schema-compliant dataset. A single validated `company-data.json` file is needed to enable downstream analysis, search, and reporting across all companies.

## What Changes

- Read all 306 company folders and their contents (`company-info.md`, `company-people.json`, `social-profile-scraped.json`, `social-profiles.md`)
- Extract and normalize company information into a strict JSON schema
- Normalize domain labels consistently across all companies (e.g., "Software Development" → "Software & IT Services")
- Extract products/services with type classification (product/service, b2b/b2c)
- Map people data including social profiles (LinkedIn, Twitter) with availability flags
- Handle sales data with date type classification (year/quarter/range)
- Validate JSON structure and schema compliance every 5 companies
- Output a single `company-data.json` containing all 306 companies

## Capabilities

### New Capabilities
- `data-extraction`: Reading company folders, parsing files (markdown + JSON), and mapping content to the output schema
- `domain-normalization`: Consistent domain label normalization across all 306 companies using defined cluster rules
- `json-validation`: Schema validation and structural integrity checks for the output file
- `progress-tracking`: Checklist and batch validation tracking for processing all 306 companies

### Modified Capabilities

(none - this is a new dataset creation task)

## Impact

- Creates new file: `company-data.json` at project root (~306 company objects)
- Read-only access to `companies/` directory and all 306 subfolders
- No existing code, APIs, or systems are modified
- Downstream consumers will depend on the schema defined in this output
