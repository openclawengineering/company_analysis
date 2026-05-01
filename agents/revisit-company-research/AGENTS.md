# AGENTS.md - Revisit Company Research Agent

## Mission

Revisit company research files in the GitHub repo `openclawengineering/company_analysis` to add missing data:
1. **Company Mentions** section in `company-info.md` — news, blog, and media mentions found online
2. **LinkedIn & Twitter URLs** in `company-people.json` — for people listed on company websites

## Sources of Truth

### Company List (Master)
- **Gist:** https://gist.github.com/hazrat-arisaftech/2dc68f7845553be258733cafa2cff7db
- CSV format: `SerialNo,CompanyName,Website,Address,Prefecture,BusinessFields,Features,RecruitTags,Email,Phone,Notes,LogoURL`

### GitHub Repo
- **Repo:** `openclawengineering/company_analysis`
- **Branch:** `master`
- **Local path:** `/home/openclaw_user/.openclaw/workspace/company_analysis/`

## File Formats

### company-info.md
Existing format varies by company. Some are in English, some in Japanese. **Keep the existing language.**

**Add a "Company Mentions" section** at the end of the file (before any footer/notes):
```markdown
## Company Mentions

- **[Source Name]** — [Date] — [Summary of mention] ([URL](link))
```

### company-people.json
Two formats exist in the repo. Use the **newer format** (matching the example below) for all updates:

```json
{
  "company": {
    "name_jp": "あさかわシステムズ株式会社",
    "name_en": "あさかわシステムズ",
    "website": "https://www.a-sk.co.jp/company/outline/"
  },
  "people": [
    {
      "name": "三宅",
      "title": "代表取締役社長",
      "linkedin": null,
      "twitter": "https://x.com/m3_myk",
      "department": "",
      "email": ""
    }
  ],
  "social_profiles": [
    {
      "name": "三宅",
      "title": "代表取締役社長",
      "linkedin": null,
      "twitter": "https://x.com/m3_myk",
      "department": "",
      "email": ""
    }
  ],
  "last_updated": "2026-04-30"
}
```

**Key rules for company-people.json:**
- `people` array: ALL people found on the company website (officers, directors, executives)
- `social_profiles` array: ONLY people where we found at least one social profile URL (linkedin OR twitter)
- `linkedin`: full LinkedIn profile URL or `null`
- `twitter`: full X/Twitter profile URL or `null`
- Always update `last_updated` to current date
- Include the company website URL in `company.website`

## Workflow (Per Batch of 10)

### Step 1: Identify Companies
Take the next 10 companies from the gist CSV (by serial number). Find their corresponding folder/file in the repo.

### Step 2: For Each Company

#### a) Scrape Company Website for People
- Visit the company's official website (from gist)
- Navigate to 会社概要 (Company Overview), 役員紹介 (Officers), 組織図 (Organization) pages
- Extract names, titles, departments
- For companies that only have a single `.md` file (no folder), create a folder and move/restructure

#### b) Search People Online for Social Profiles
- Search: `[name] [company name] LinkedIn`
- Search: `[name] [company name] Twitter` or `[name] [company name] X`
- Search: `[name] [company name] 役員`
- For Japanese names, try full name + company, and also surname only + company
- Check LinkedIn Japan specifically: `site:jp.linkedin.com "[name]" "[company]"`
- Check X/Twitter: `site:x.com "[name]"` or `site:twitter.com "[name]"`
- **Only include verified URLs** — don't guess or fabricate

#### c) Search for Company Mentions
- Search: `"[company name]" ニュース` (news)
- Search: `"[company name]" blog`
- Search: `"[company name]" 採用` (recruiting — often has articles)
- Search: `"[company name]" プレスリリース` (press releases)
- Check: PR Times, @Press, Yahoo News, ITmedia, TechCrunch Japan, etc.
- Include mentions with date, source, summary, and URL
- **Only include substantive mentions** — not just directory listings or job postings

#### d) Update Files
- Add "Company Mentions" section to `company-info.md`
- Create/update `company-people.json` with the correct format
- If company only has a single `.md`, create a folder structure: `会社名/company-info.md` + `会社名/company-people.json`

### Step 3: Push to GitHub
```bash
cd /home/openclaw_user/.openclaw/workspace/company_analysis
git add -A
git commit -m "Batch X: Updated company mentions and people profiles for companies N-M"
git push origin master
```

### Step 4: Report
Notify the user after each batch of 10 is pushed.

## Language Rules
- If the existing `company-info.md` is in **English**, add mentions in **English**
- If the existing `company-info.md` is in **Japanese**, add mentions in **Japanese**
- `company-people.json` field names stay in English (format standard)
- People names stay in Japanese as found on the website

## Priority Order
Process companies by their serial number from the gist (1, 2, 3...).

## Companies That Need Folder Restructuring
Some companies exist only as a single `.md` file (e.g., `104_アークシステム_ArcSystem.md`). These need to be converted to folder format:
- Create folder: `アークシステム/`
- Move/rename: `company-info.md` inside it
- Create: `company-people.json` inside it

## Red Lines
- **Don't fabricate data.** null > wrong URL
- **Don't delete existing content.** Only add/update
- **Cite sources.** Always include URLs for mentions
- **Respect language.** Match existing file language
- **Don't spend too long on one company.** If a website is down or no data is findable after 2-3 searches, note it and move on
