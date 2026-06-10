## ADDED Requirements

### Requirement: Domain inference from business descriptions
The system SHALL infer `company_domains` from business field descriptions, services, and keywords found in `company-info.md`.

#### Scenario: Recognized Japanese business keywords
- **WHEN** company-info.md contains known Japanese business domain keywords (e.g., "SES", "受託開発", "パッケージソフトウェア", "クラウド")
- **THEN** each keyword is mapped to its normalized English domain name in the `company_domains` array

#### Scenario: Unrecognized or ambiguous keywords
- **WHEN** a business keyword does not match the curated mapping
- **THEN** the system uses contextual understanding to assign the most appropriate domain, defaulting to a reasonable category

### Requirement: Domain name normalization
All domain names SHALL use a consistent English naming convention. The same business domain MUST always produce the same normalized string.

#### Scenario: Same domain across companies
- **WHEN** two different companies both describe "受託開発" (custom software development)
- **THEN** both companies have the identical string in their `company_domains` array (e.g., "Custom Software Development")

#### Scenario: Multiple domains for one company
- **WHEN** a company operates in multiple business areas
- **THEN** all applicable domains are listed in the `company_domains` array without duplicates
