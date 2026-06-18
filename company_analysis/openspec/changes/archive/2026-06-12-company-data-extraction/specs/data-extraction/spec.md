## ADDED Requirements

### Requirement: Read all company folders and files
The system SHALL iterate over every folder inside the `companies/` directory (306 total) and read all files within each folder. File types include `company-info.md`, `company-info-en.md`, `company-people.json`, `social-profile-scraped.json`, and `social-profiles.md`.

#### Scenario: Folder with all file types present
- **WHEN** a company folder contains `company-info.md`, `company-info-en.md`, `company-people.json`, `social-profile-scraped.json`, and `social-profiles.md`
- **THEN** the system SHALL read and parse all five files, extracting data from each

#### Scenario: Folder with minimal files
- **WHEN** a company folder contains only `company-info.md` and `company-people.json`
- **THEN** the system SHALL extract data from available files and use `null` or `[]` for missing data fields

#### Scenario: Missing optional files
- **WHEN** `social-profile-scraped.json` or `social-profiles.md` do not exist in a folder
- **THEN** the system SHALL proceed without error, leaving social profile fields with `profile_available: false`

### Requirement: Map company folder name to output
The system SHALL set `company_folder_name` to the exact directory name of the company folder.

#### Scenario: Standard folder naming
- **WHEN** a folder is named `アリサフテックジャパン_ArisaftechJapan`
- **THEN** `company_folder_name` SHALL be `アリサフテックジャパン_ArisaftechJapan`

### Requirement: Extract company names
The system SHALL extract `company_name_en` (English name) and `company_name_jp` (Japanese name) from the source files. The English name MAY be parsed from the folder name suffix or from the info markdown.

#### Scenario: Names available in company-info.md
- **WHEN** the info file contains both Japanese and English company names
- **THEN** both `company_name_jp` and `company_name_en` SHALL be populated

#### Scenario: Only Japanese name available
- **WHEN** no English name is found in any source file
- **THEN** `company_name_en` SHALL be `null` and `company_name_jp` SHALL be populated

### Requirement: Extract company profile fields
The system SHALL extract address, phone, fax, founded date, established date, capital, and number of employees into the `company_profile` object.

#### Scenario: Full profile available
- **WHEN** source files contain address, phone, fax, founded, established, capital, and employee count
- **THEN** all fields in `company_profile` SHALL be populated with their values

#### Scenario: Partial profile data
- **WHEN** only some profile fields are available in source files
- **THEN** available fields SHALL be populated and missing fields SHALL be `null`

### Requirement: Extract sales data
The system SHALL extract sales figures into the `sales` array, each with `date_type` (year, quarter, or range), `date`, and `total_sales`.

#### Scenario: Annual sales data
- **WHEN** a company reports annual revenue (e.g., "2023年: 5億円")
- **THEN** a sales entry SHALL be created with `date_type: "year"`, `date: "2023"`, and `total_sales: "5億円"`

#### Scenario: Quarterly sales data
- **WHEN** quarterly figures are available
- **THEN** entries SHALL use `date_type: "quarter"` with the appropriate date label

#### Scenario: No sales data
- **WHEN** no sales information exists in source files
- **THEN** `sales` SHALL be `[]`

### Requirement: Extract products and services
The system SHALL extract product and service entries into `products_and_services`, each with `name`, `type` (product or service), `client_type` (b2b or b2c), `description`, and `target_demography`.

#### Scenario: Products listed in source
- **WHEN** a company's info file describes specific software products
- **THEN** each product SHALL be extracted with `type: "product"` and inferred `client_type`

#### Scenario: Services described in source
- **WHEN** a company provides IT consulting or system integration services
- **THEN** each service SHALL be extracted with `type: "service"` and appropriate `client_type`

#### Scenario: No product/service evidence
- **WHEN** no products or services can be identified from source files
- **THEN** `products_and_services` SHALL be `[]`

### Requirement: Extract people data
The system SHALL extract people from `company-people.json` and supplement with social profile data. Each person SHALL have `name_en`, `name_jp`, `title`, `notes`, `linkedin`, and `twitter_url`.

#### Scenario: Person with full data
- **WHEN** a person has Japanese name, English name, title, and social profiles
- **THEN** all fields SHALL be populated with `profile_available: true` where URLs exist and `data_available: true` where profiles were parsed

#### Scenario: Person with no social profiles
- **WHEN** a person has name and title but no social media links
- **THEN** `linkedin.profile_available` and `twitter_url.profile_available` SHALL both be `false`

### Requirement: Extract partners, certifications, links, and tech stack
The system SHALL extract partners, certifications, external links, and tech stack from all available source files.

#### Scenario: Partners listed in info file
- **WHEN** a company lists partner companies
- **THEN** each partner SHALL be added to the `partners` array

#### Scenario: Tech stack evidence found
- **WHEN** source files mention specific programming languages, frameworks, or infrastructure tools
- **THEN** each identified technology SHALL be added to `tech_stack`

#### Scenario: No data for optional arrays
- **WHEN** no partners, certifications, links, or tech stack are found
- **THEN** each array SHALL be `[]`

### Requirement: Output single JSON file
All 306 company objects SHALL be written to a single `company-data.json` file as a top-level JSON array.

#### Scenario: Complete output
- **WHEN** all 306 companies have been processed
- **THEN** `company-data.json` SHALL contain a valid JSON array with exactly 306 objects
