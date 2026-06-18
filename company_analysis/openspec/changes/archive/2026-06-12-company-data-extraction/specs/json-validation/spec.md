## ADDED Requirements

### Requirement: Validate JSON structure every 5 companies
The system SHALL validate the JSON output after every 5 companies are processed. Validation MUST pass before proceeding to the next batch.

#### Scenario: Batch of 5 companies completes
- **WHEN** 5 companies have been added to `company-data.json`
- **THEN** the system SHALL validate the entire JSON structure and confirm validity before processing the next company

#### Scenario: Validation detects schema violation
- **WHEN** a company object is missing a required top-level field or has an invalid field type
- **THEN** the system SHALL fix the error before continuing to the next company

### Requirement: Schema compliance for every company object
Each company object in the output SHALL conform to the strict output schema: all required fields present, correct types (strings, arrays, objects, nulls), and valid enum values where applicable.

#### Scenario: Valid company object
- **WHEN** a company object has all required fields with correct types
- **THEN** validation SHALL pass for that object

#### Scenario: Invalid enum in products
- **WHEN** a product entry has `type: "subscription"` (not a valid enum value)
- **THEN** validation SHALL reject the entry and require correction to "product" or "service"

### Requirement: No null arrays
Array fields (`company_domains`, `products_and_services`, `people`, `partners`, `certifications`, `links`, `tech_stack`, `sales`) SHALL be `[]` when empty, never `null`.

#### Scenario: Empty arrays validated
- **WHEN** a company has no partners
- **THEN** `partners` SHALL be `[]`, and validation SHALL reject `null`

### Requirement: Final output validation
After all 306 companies are processed, the system SHALL perform a final validation of the complete `company-data.json` file.

#### Scenario: Final validation passes
- **WHEN** all 306 companies are processed
- **THEN** the system SHALL validate the entire file and confirm it is valid JSON with exactly 306 objects, all schema-compliant

#### Scenario: Final validation fails
- **WHEN** the final validation detects any error
- **THEN** all errors SHALL be listed and fixed before the task is considered complete
