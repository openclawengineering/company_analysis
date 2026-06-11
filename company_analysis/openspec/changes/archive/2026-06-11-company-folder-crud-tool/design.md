## Context

The project has 306 company entries in `company-data.json`, each identified by a `company_folder_name` that maps to a physical directory (e.g., `43_株式会社アルファ・ウェーブ_AlphaWave`). Each folder contains source files like `company-info.md`, `company-people.json`, and `social-profile-scraped.json`. There is currently no way to quickly target a single company for inspection, verification, or modification without loading and scanning the entire dataset.

## Goals / Non-Goals

**Goals:**
- Provide a single CLI entry point (`company_tool.py`) for all company data operations
- Use `company_folder_name` as the primary lookup key for instant O(1) access
- Support read, verify, update, delete, and list operations
- Keep it dependency-free (Python standard library only)

**Non-Goals:**
- No web API or server — this is a CLI-only tool
- No batch operations across multiple companies in a single invocation
- No schema migration or structural changes to `company-data.json`
- No interactive mode or TUI

## Decisions

### 1. CLI structure: subcommands via argparse

**Decision:** Use `argparse` with subcommands (`read`, `verify`, `update`, `delete`, `list`).

**Rationale:** Subcommands map cleanly to CRUD operations and provide built-in help text. Each subcommand has its own arguments, avoiding flag collision.

**Alternative considered:** A single command with `--operation` flag — rejected because it makes argument parsing complex and help text confusing.

### 2. Data storage: in-memory index built on load

**Decision:** Load `company-data.json` once into a list, build a `dict` index mapping `company_folder_name` → entry position for O(1) lookups.

**Rationale:** The file is ~670KB (306 entries). Loading it fully is trivial. An in-memory index avoids repeated linear scans and keeps the implementation simple.

**Alternative considered:** SQLite or a separate index file — rejected as over-engineering for 306 records.

### 3. Verify command: field-level cross-checks

**Decision:** The `verify` command accepts a `--field` argument (e.g., `company_domains`, `company_profile`, `people`) and checks that field's data against the corresponding source files in the company folder.

**Rationale:** Field-level verification lets the user target exactly what they want to validate without running a full audit every time.

### 4. Update command: JSON patch via dot-path notation

**Decision:** Use `--field` and `--value` arguments where field supports dot-path notation (e.g., `company_profile.address`, `company_domains` with `--append`).

**Rationale:** Dot-path notation is intuitive and covers nested fields. `--append` flag handles list fields like `company_domains` without requiring JSON array syntax on the command line.

**Alternative considered:** Full JSON patch (RFC 6902) — rejected as too complex for a CLI tool.

### 5. Partial/fuzzy name matching for convenience

**Decision:** The `--name` argument for folder name lookup supports partial matching. If an exact match isn't found, search for substrings and show matches. Require exact match for update/delete to prevent accidents.

**Rationale:** Users won't always remember the full folder name. Partial matching is helpful for read/verify but should be strict for destructive operations.

## Risks / Trade-offs

- **[Concurrent writes]** If two processes run update/delete simultaneously, one may overwrite the other's changes. → Mitigation: not a concern for single-user CLI usage. Document that the tool is not safe for concurrent use.
- **[Large value input]** Multi-line or complex values (e.g., full addresses with special characters) may be awkward to pass via CLI arguments. → Mitigation: accept `--value-from-file` for complex updates.
- **[Fuzzy match false positives]** Partial name matching could return unexpected results. → Mitigation: always show the matched folder name and require confirmation before update/delete.
