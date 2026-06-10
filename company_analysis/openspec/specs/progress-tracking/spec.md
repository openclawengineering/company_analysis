## ADDED Requirements

### Requirement: Company checklist in tasks.md
The system SHALL maintain a checklist of all 306 company folders in `tasks.md`, with each company as a checkbox item.

#### Scenario: Initial checklist creation
- **WHEN** the extraction process begins
- **THEN** `tasks.md` contains 306 checkbox items, all unchecked `[ ]`

#### Scenario: Marking a company as complete
- **WHEN** a company folder has been fully processed and its data added to `company-data.json`
- **THEN** the corresponding checkbox is updated to `[x]`

### Requirement: Progress visibility
The checklist SHALL provide a clear view of how many companies have been completed vs remaining.

#### Scenario: Checking progress
- **WHEN** the user reviews the tasks file
- **THEN** completed companies are marked `[x]` and pending are `[ ]`, making it easy to see what's left
