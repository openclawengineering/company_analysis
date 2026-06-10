## Context

306 company folders exist under `company_analysis/`, each named with a mix of Japanese and English names. Each folder contains:
- `company-info.md` (306/306) — Markdown with company overview, address, business fields, etc. Many are placeholder files with minimal data.
- `company-people.json` (306/306) — JSON with people list, often empty.
- `social-profiles.md` (165/306) — Markdown with LinkedIn/Twitter profile URLs.
- `social-profile-scraped.json` (165/306) — JSON with scraped LinkedIn/Twitter data.

The target schema is defined in `json-structure.md`. Output goes to a single `company-data.json` file at project root.

## Goals / Non-Goals

**Goals:**
- Consolidate all 306 companies into one well-structured JSON file
- Extract all available data from source files, mapping to the target schema
- Infer and normalize `company_domains` from business descriptions
- Validate output structure periodically during extraction
- Track per-company progress in a checklist

**Non-Goals:**
- Re-scraping or fetching new data from the web
- Enhancing placeholder company-info.md files with external data
- Building a UI or API on top of the data
- Deduplicating companies that appear under different folder names

## Decisions

### 1. Batch processing with incremental JSON updates
**Decision**: Process one folder at a time, append to `company-data.json` after each extraction.
**Rationale**: Allows progress tracking and recovery from interruptions without re-processing completed companies.
**Alternative**: Process all at once and write once — rejected because a crash would lose all progress.

### 2. JSON validation script runs every 5 companies
**Decision**: A standalone Python script (`validate_json.py`) validates the structure.
**Rationale**: Catches formatting errors early without waiting until all 306 are done. Lightweight check of required fields, types, and list structures.

### 3. Domain normalization via a curated mapping
**Decision**: Maintain a dictionary of known Japanese business domain terms → normalized English domain names. AI infers domains at extraction time.
**Rationale**: Japanese IT companies use a relatively small set of domain keywords (SES, 受託開発, パッケージソフトウェア, etc.). A mapping ensures consistency.
**Alternative**: Free-text AI inference per company — rejected because it leads to inconsistent naming across companies.

### 4. Progress tracking in tasks.md checklist
**Decision**: Use the OpenSpec tasks.md file to maintain a `[x]` / `[ ]` checkbox list per company.
**Rationale**: Keeps progress visible alongside other change artifacts. Easy to scan completion percentage.

## Risks / Trade-offs

- **Placeholder files**: Many `company-info.md` files are placeholders with no real data → Resulting JSON entries will have mostly `null` fields. This is acceptable — the schema handles it.
- **Inconsistent Japanese naming**: Company folder names and internal file data may vary → Use folder name as `company_folder_name` and extract `company_name_en` / `company_name_jp` from file content.
- **Large JSON file**: 306 companies with full data could be 500KB+ → Acceptable for the use case. No streaming or chunking needed.
- **AI inference for domains**: May occasionally misclassify → Mitigated by using a curated mapping and reviewing during validation.
