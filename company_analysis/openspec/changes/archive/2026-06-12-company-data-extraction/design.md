## Context

The project has a `companies/` directory with 306 subfolders. Each folder contains a mix of markdown (company info in Japanese and/or English) and JSON (people data, social profiles) files. The current state is entirely unstructured - there is no unified dataset. The goal is to produce a single `company-data.json` that consolidates all company information into a strict JSON schema.

This is a manual extraction task carried out by an AI agent reading each folder's files and producing structured output. No automated scripts are involved - the system prompt explicitly forbids generating automation scripts.

## Goals / Non-Goals

**Goals:**
- Process all 306 companies into a single schema-compliant `company-data.json`
- Normalize domain labels consistently using a predefined cluster mapping
- Validate output integrity every 5 companies
- Maintain a visible progress checklist
- Preserve all available data (Japanese names, English names, social profiles, sales figures)

**Non-Goals:**
- Building automated extraction scripts or pipelines
- Modifying source files in `companies/`
- Deduplicating or merging companies across folders
- Enriching data with external sources (web scraping, API calls)
- Creating multiple output files

## Decisions

### Decision 1: Batch processing in groups of 5
Process companies in batches of 5, validating after each batch. This balances throughput with error detection - catching schema violations early prevents compounding errors across hundreds of companies.

**Alternative considered**: Validate only at the end. Rejected because fixing 306 companies worth of accumulated errors would be far more costly than incremental fixes.

### Decision 2: Domain normalization via predefined cluster map
Use a fixed mapping table of raw domain terms to normalized cluster labels. The core clusters are:
- `Software & IT Services` ← Software Development, IT Consulting, System Integration, SIer, etc.
- `Insurance` ← Insurance Brokerage, Insurance Agency, Risk Insurance, etc.
- `Financial Services` ← Investment Advisory, Wealth Management, Asset Management, etc.

Additional clusters will be discovered during processing and added to the map to ensure consistency.

**Alternative considered**: LLM-inferred domains per company. Rejected because it risks inconsistency across 306 companies. A fixed map guarantees the same raw term always maps to the same label.

### Decision 3: People data merged from multiple sources
People data comes from `company-people.json` (structured) and `social-profile-scraped.json` (social profile details). Merge by matching on person name, with `company-people.json` as the primary source and social profiles as supplementary.

### Decision 4: Markdown parsing approach for company-info.md
Company info files are semi-structured markdown with headings, tables, and free text. Extract structured fields by identifying known patterns (e.g., "所在地" → address, "設立" → established date, "資本金" → capital, "従業員数" → employee count). Falls back to scanning for field labels when standard patterns don't match.

### Decision 5: Output schema as single JSON array
Write the entire output as one JSON array to a single file. This keeps the output simple and self-contained for downstream consumers.

**Alternative considered**: One file per company with an index. Rejected because the system prompt requires a single output file.

## Risks / Trade-offs

- **[306 companies is a large volume]** → Batch processing with validation checkpoints prevents catastrophic data loss. Progress checklist allows resuming from last validated point.
- **[Inconsistent markdown formatting across folders]** → Flexible field extraction with fallback patterns. Manual review of edge cases during validation.
- **[New domain clusters discovered mid-processing]** → Cluster map is extensible. New domains found during extraction are added to the map and retroactively checked for consistency.
- **[Social profile data may be incomplete]** → `profile_available` / `data_available` flags distinguish between "no profile found" and "profile found but couldn't parse". This prevents false negatives.
- **[Japanese text encoding issues]** → All files are read as UTF-8. Company folder names contain full-width characters and must be preserved exactly.
