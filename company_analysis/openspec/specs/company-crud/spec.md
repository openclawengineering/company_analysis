## ADDED Requirements

### Requirement: Load and index company data
The tool SHALL load `company-data.json` on startup and build an in-memory index mapping each `company_folder_name` to its entry for O(1) lookup.

#### Scenario: Successful data load
- **WHEN** the tool starts and `company-data.json` exists and is valid JSON
- **THEN** all company entries are loaded and indexed by `company_folder_name`

#### Scenario: Missing data file
- **WHEN** `company-data.json` does not exist in the working directory
- **THEN** the tool SHALL print an error message and exit with a non-zero status code

### Requirement: Read company entry by folder name
The tool SHALL accept a `read` subcommand with a `--name` argument containing a `company_folder_name` and display the full JSON entry for that company.

#### Scenario: Exact match found
- **WHEN** the user runs `company_tool.py read --name "43_株式会社アルファ・ウェーブ_AlphaWave"`
- **THEN** the tool SHALL display the complete JSON entry for that company formatted as readable output

#### Scenario: Partial match returns candidates
- **WHEN** the user runs `company_tool.py read --name "AlphaWave"` and no exact match exists but one or more entries contain "AlphaWave" as a substring
- **THEN** the tool SHALL display all matching company entries with their `company_folder_name` and `company_name_en`

#### Scenario: No match found
- **WHEN** the user runs `company_tool.py read --name "NonExistentCompany"` and no exact or partial match exists
- **THEN** the tool SHALL print "No company found matching 'NonExistentCompany'" and exit with a non-zero status code

### Requirement: Verify company fields against source files
The tool SHALL accept a `verify` subcommand with `--name` and optional `--field` arguments. It SHALL cross-check the specified field's data in `company-data.json` against the corresponding source files in the company's physical folder.

#### Scenario: Verify company_domains
- **WHEN** the user runs `company_tool.py verify --name "<folder_name>" --field company_domains`
- **THEN** the tool SHALL read `company-info.md` from the company folder, extract the domain information, and report whether the domains in `company-data.json` match the source file

#### Scenario: Verify company_profile
- **WHEN** the user runs `company_tool.py verify --name "<folder_name>" --field company_profile`
- **THEN** the tool SHALL read `company-info.md` from the company folder, extract profile fields (address, phone, capital, etc.), and report discrepancies against `company-data.json`

#### Scenario: Verify people
- **WHEN** the user runs `company_tool.py verify --name "<folder_name>" --field people`
- **THEN** the tool SHALL read `company-people.json` from the company folder and report whether people entries match between the source and `company-data.json`

#### Scenario: Verify all fields
- **WHEN** the user runs `company_tool.py verify --name "<folder_name>"` without `--field`
- **THEN** the tool SHALL verify all supported fields and report discrepancies for each

#### Scenario: Company folder not found
- **WHEN** the user runs `company_tool.py verify --name "<folder_name>"` and the physical folder does not exist on disk
- **THEN** the tool SHALL print a warning that the source folder is missing and report that verification cannot be performed

### Requirement: Update company entry fields
The tool SHALL accept an `update` subcommand with `--name`, `--field`, and `--value` arguments. It SHALL modify the specified field in the matching company entry and write the updated data back to `company-data.json`.

#### Scenario: Update a simple field
- **WHEN** the user runs `company_tool.py update --name "<folder_name>" --field company_name_en --value "New Name"`
- **THEN** the tool SHALL update the `company_name_en` field, write the full JSON back to `company-data.json`, and print a confirmation

#### Scenario: Update a nested field using dot-path
- **WHEN** the user runs `company_tool.py update --name "<folder_name>" --field company_profile.address --value "New Address"`
- **THEN** the tool SHALL update the nested `address` field within `company_profile` and save the change

#### Scenario: Append to a list field
- **WHEN** the user runs `company_tool.py update --name "<folder_name>" --field company_domains --value "AI" --append`
- **THEN** the tool SHALL append "AI" to the `company_domains` list and save the change

#### Scenario: Update requires exact folder name match
- **WHEN** the user runs `company_tool.py update --name "AlphaWave"` and only a partial match is found
- **THEN** the tool SHALL refuse the update, print the matched folder names, and instruct the user to provide an exact `company_folder_name`

#### Scenario: Update with value from file
- **WHEN** the user runs `company_tool.py update --name "<folder_name>" --field company_profile --value-from-file profile.json`
- **THEN** the tool SHALL read the JSON content from `profile.json` and use it as the new value for the field

#### Scenario: Invalid field path
- **WHEN** the user runs `company_tool.py update --name "<folder_name>" --field nonexistent.field --value "x"`
- **THEN** the tool SHALL print an error that the field path does not exist and exit without modifying the file

### Requirement: Delete company entry
The tool SHALL accept a `delete` subcommand with a `--name` argument. It SHALL remove the matching company entry from `company-data.json` after confirmation.

#### Scenario: Successful deletion
- **WHEN** the user runs `company_tool.py delete --name "<folder_name>"` with an exact match
- **THEN** the tool SHALL prompt for confirmation, remove the entry on confirmation, write the updated JSON back to `company-data.json`, and print a confirmation

#### Scenario: Delete requires exact match
- **WHEN** the user runs `company_tool.py delete --name "AlphaWave"` and only a partial match is found
- **THEN** the tool SHALL refuse the deletion and print the matched folder names

#### Scenario: Delete cancelled by user
- **WHEN** the tool prompts for confirmation and the user declines
- **THEN** the tool SHALL print "Delete cancelled" and exit without modifying the file

### Requirement: List company folder names
The tool SHALL accept a `list` subcommand that displays all `company_folder_name` values from `company-data.json`.

#### Scenario: List all companies
- **WHEN** the user runs `company_tool.py list`
- **THEN** the tool SHALL display all `company_folder_name` values, one per line, sorted alphabetically

#### Scenario: Filter by domain
- **WHEN** the user runs `company_tool.py list --domain "System Development"`
- **THEN** the tool SHALL display only companies whose `company_domains` list includes "System Development"

#### Scenario: No companies match filter
- **WHEN** the user runs `company_tool.py list --domain "NonExistentDomain"` and no companies match
- **THEN** the tool SHALL print "No companies found with domain 'NonExistentDomain'"
