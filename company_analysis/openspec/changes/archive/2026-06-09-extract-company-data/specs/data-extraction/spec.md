## ADDED Requirements

### Requirement: Extract company profile from source files
The system SHALL read `company-info.md` from each company folder and extract company name (English and Japanese), address, phone, fax, founded date, established date, capital, number of employees, and sales data into structured fields per the `json-structure.md` schema.

#### Scenario: Full data extraction from a complete company-info.md
- **WHEN** a company folder contains a `company-info.md` with full company details
- **THEN** all available fields are populated in the JSON entry and missing optional fields are set to `null`

#### Scenario: Placeholder company-info.md file
- **WHEN** a company folder contains a placeholder `company-info.md` with no real data
- **THEN** the JSON entry is created with `company_folder_name`, `company_name_en`, `company_name_jp` extracted from the folder name or file header, and all other fields set to `null`

### Requirement: Extract people data from company-people.json
The system SHALL read `company-people.json` and map people entries to the `people` array with `name_en`, `name_jp`, `title`, and `notes` fields.

#### Scenario: People list with entries
- **WHEN** `company-people.json` contains a non-empty people array
- **THEN** each person is mapped to the people array with all available fields populated

#### Scenario: Empty people list
- **WHEN** `company-people.json` contains an empty people array
- **THEN** the people field is set to an empty list `[]`

### Requirement: Merge social profile data
The system SHALL read `social-profiles.md` and `social-profile-scraped.json` when available, and merge LinkedIn/Twitter URLs and scraped data into the corresponding person entries in the `people` array.

#### Scenario: Social profiles available
- **WHEN** a company folder contains `social-profile-scraped.json` with LinkedIn/Twitter data
- **THEN** matching people entries receive `linkedin` and `twitter_url` objects with `profile_available`, `data_available`, and `url` fields populated

#### Scenario: No social profiles available
- **WHEN** a company folder does not contain social profile files
- **THEN** people entries have `linkedin` and `twitter_url` fields set with `profile_available: false`, `data_available: false`, `url: null`

### Requirement: Extract products and services
The system SHALL extract products and services from `company-info.md` business descriptions, mapping each to an object with `name`, `type` (product/service), `client_type` (b2b/b2c), `description`, and `target_demography`.

#### Scenario: Services described in company info
- **WHEN** company-info.md lists business services or products
- **THEN** each is added to the `products_and_services` array with available fields populated

### Requirement: Extract additional company metadata
The system SHALL extract partners, certifications, links, and tech stack from `company-info.md` when available.

#### Scenario: Partners and certifications listed
- **WHEN** company-info.md mentions partner companies or certifications
- **THEN** they are added to the respective `partners` and `certifications` arrays

### Requirement: Single output file
All company data SHALL be written to a single `company-data.json` file at the project root, containing a JSON array of company objects.

#### Scenario: All companies in one file
- **WHEN** extraction is complete
- **THEN** `company-data.json` contains a JSON array with exactly one entry per company folder
