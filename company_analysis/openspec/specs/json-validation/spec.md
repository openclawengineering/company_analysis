## ADDED Requirements

### Requirement: Validate JSON structure
The system SHALL provide a validation script that checks `company-data.json` conforms to the schema defined in `json-structure.md`.

#### Scenario: Valid JSON file
- **WHEN** the validation script is run on a well-formed `company-data.json`
- **THEN** the script reports success with the count of valid company entries

#### Scenario: Missing required fields
- **WHEN** a company entry is missing required fields (e.g., `company_folder_name`)
- **THEN** the script reports the specific company and missing field

### Requirement: Validate field types
The validation script SHALL check that each field matches its expected type (string, number, list, object, null).

#### Scenario: Incorrect field type
- **WHEN** a field that should be a list contains a string
- **THEN** the script reports the company, field name, expected type, and actual type

### Requirement: Validate list entry structure
The validation script SHALL check that entries in `products_and_services`, `people`, `sales`, and `links` arrays have the correct sub-fields.

#### Scenario: Malformed people entry
- **WHEN** a person object is missing required sub-fields
- **THEN** the script reports the company and specific person entry that is malformed

### Requirement: Periodic validation during extraction
The validation script SHALL be runnable after every 5 company extractions to catch errors early.

#### Scenario: Mid-extraction validation
- **WHEN** 5 companies have been processed
- **THEN** running the validation script confirms the JSON is well-formed so far
