## 1. Core Data Layer

- [x] 1.1 Create `company_tool.py` with data loading function that reads `company-data.json` and returns the parsed JSON list
- [x] 1.2 Implement `build_index()` function that creates a dict mapping `company_folder_name` → list index for O(1) lookup
- [x] 1.3 Implement `save_data()` function that writes the full JSON list back to `company-data.json` with proper formatting
- [x] 1.4 Implement `find_company()` helper that tries exact match first, then partial substring match, returning match type and results
- [x] 1.5 Implement `get_nested_field()` and `set_nested_field()` helpers for dot-path field access (e.g., `company_profile.address`)

## 2. CLI Setup

- [x] 2.1 Set up argparse with `read`, `verify`, `update`, `delete`, `list` subcommands and their respective arguments
- [x] 2.2 Add `--name` argument to `read`, `verify`, `update`, `delete` subcommands
- [x] 2.3 Add `--field`, `--value`, `--append`, `--value-from-file` arguments to `update` subcommand
- [x] 2.4 Add `--field` optional argument to `verify` subcommand
- [x] 2.5 Add `--domain` optional filter argument to `list` subcommand
- [x] 2.6 Add error handling for missing `company-data.json` with non-zero exit code

## 3. Read Command

- [x] 3.1 Implement `cmd_read()` — exact match displays full JSON entry with pretty formatting
- [x] 3.2 Handle partial matches — display `company_folder_name` and `company_name_en` for all candidates
- [x] 3.3 Handle no match — print "No company found matching '<name>'" and exit with non-zero code

## 4. Verify Command

- [x] 4.1 Implement `cmd_verify()` dispatcher that runs specific verifiers based on `--field` or all verifiers if omitted
- [x] 4.2 Implement `verify_domains()` — read `company-info.md` from company folder, extract domain info, compare against `company_domains` in JSON
- [x] 4.3 Implement `verify_profile()` — read `company-info.md`, extract profile fields, compare against `company_profile` in JSON
- [x] 4.4 Implement `verify_people()` — read `company-people.json` from company folder, compare people entries against JSON
- [x] 4.5 Handle missing company folder on disk — print warning that source folder is missing

## 5. Update Command

- [x] 5.1 Implement `cmd_update()` with exact-match-only requirement (reject partial matches, show candidates)
- [x] 5.2 Implement dot-path field update using `set_nested_field()` helper
- [x] 5.3 Implement `--append` flag for list fields — append value to existing list
- [x] 5.4 Implement `--value-from-file` — read JSON content from a file and use as field value
- [x] 5.5 Validate field path exists before modifying — print error and exit if path is invalid
- [x] 5.6 Write updated JSON back to `company-data.json` and print confirmation

## 6. Delete Command

- [x] 6.1 Implement `cmd_delete()` with exact-match-only requirement
- [x] 6.2 Add confirmation prompt before deletion — "Are you sure you want to delete <name>? (y/N)"
- [x] 6.3 Handle user declining — print "Delete cancelled" and exit
- [x] 6.4 Remove entry from list, write back to `company-data.json`, and print confirmation

## 7. List Command

- [x] 7.1 Implement `cmd_list()` — display all `company_folder_name` values sorted alphabetically
- [x] 7.2 Implement `--domain` filter — show only companies whose `company_domains` includes the given domain
- [x] 7.3 Handle no matches for domain filter — print "No companies found with domain '<domain>'"
