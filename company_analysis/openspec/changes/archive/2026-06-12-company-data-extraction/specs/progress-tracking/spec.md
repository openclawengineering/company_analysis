## ADDED Requirements

### Requirement: Maintain processing checklist
The system SHALL maintain a checklist tracking which companies have been successfully processed and validated.

#### Scenario: Company processed successfully
- **WHEN** a company's data has been extracted, mapped to schema, and appended to `company-data.json`
- **THEN** the checklist SHALL mark that company as complete

#### Scenario: Company processing incomplete
- **WHEN** a company has not yet been processed
- **THEN** the checklist SHALL show that company as incomplete

### Requirement: Checklist completion criteria
A company SHALL only be marked complete when its JSON has been added to `company-data.json` AND validation has passed.

#### Scenario: JSON added but not validated
- **WHEN** a company's JSON is appended but validation has not yet run
- **THEN** the company SHALL NOT be marked complete until the next validation checkpoint passes

### Requirement: Full completion verification
The task is complete only when the checklist shows all 306 companies processed, `company-data.json` is valid JSON, schema is fully respected, and domain normalization is consistent.

#### Scenario: All companies processed
- **WHEN** the checklist shows all 306 companies complete and final validation passes
- **THEN** the task SHALL be considered complete
