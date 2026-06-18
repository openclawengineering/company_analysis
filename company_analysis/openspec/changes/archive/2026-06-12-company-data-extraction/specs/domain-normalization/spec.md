## ADDED Requirements

### Requirement: Normalize company domains to cluster labels
The system SHALL map raw domain descriptions (e.g., "Software Development", "IT Consulting", "System Integration") to normalized cluster labels defined in the domain normalization rules.

#### Scenario: Software and IT cluster
- **WHEN** a company's domain is described as "Software Development", "IT Consulting", "System Integration", or similar IT-related terms
- **THEN** the `company_domains` array SHALL contain `"Software & IT Services"`

#### Scenario: Insurance cluster
- **WHEN** a company's domain includes "Insurance Brokerage", "Insurance Agency", or "Risk Insurance"
- **THEN** the `company_domains` array SHALL contain `"Insurance"`

#### Scenario: Finance cluster
- **WHEN** a company's domain includes "Investment Advisory", "Wealth Management", or "Asset Management"
- **THEN** the `company_domains` array SHALL contain `"Financial Services"`

### Requirement: Multi-domain companies
A company MAY belong to multiple domain clusters. Each matching cluster SHALL be a separate entry in the `company_domains` array.

#### Scenario: Company in two domains
- **WHEN** a company operates in both software development and financial services
- **THEN** `company_domains` SHALL be `["Software & IT Services", "Financial Services"]`

### Requirement: Domain consistency across all companies
The same raw domain term SHALL always map to the same normalized label across all 306 companies. No variations or synonyms of the same cluster label are permitted.

#### Scenario: Consistent mapping
- **WHEN** company A and company B both describe their domain as "System Integration"
- **THEN** both SHALL have `"Software & IT Services"` in their `company_domains`

### Requirement: No fabricated domains
If a company's domain cannot be determined from source files, `company_domains` SHALL be `[]`. The system MUST NOT invent domains.

#### Scenario: No domain evidence
- **WHEN** a company's files contain no domain or industry information
- **THEN** `company_domains` SHALL be `[]`
