#!/usr/bin/env python3
"""
Extract company data from ~306 folders into a single company-data.json file.
"""

import json
import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(ROOT_DIR, "company-data.json")

UNAVAILABLE = {"Not available", "N/A", "n/a", "—", "-", "住所情報が必要",
               "年月情報が必要", "人数情報が必要", "代表者情報が必要", "Research Required",
               "[Research Required]", "情報が必要", "unknown", "Unknown", ""}


def is_unavailable(val):
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() in UNAVAILABLE or val.strip().startswith("Not available")
    return False


def clean(val):
    """Clean a value: return None if unavailable, otherwise strip whitespace."""
    if is_unavailable(val):
        return None
    if isinstance(val, str):
        # Remove markdown bold markers
        val = val.strip()
        val = re.sub(r'\*\*', '', val)
        return val if val else None
    return val


def clean_list(val):
    """Clean but allow empty string as valid."""
    if val is None:
        return None
    if isinstance(val, str):
        return val.strip()
    return val


# ─── Extract rich fields from any JSON dict ──────────────────────────────

def extract_rich_json_fields(data, result):
    """Extract profile/domains/tech/partners/certs from rich JSON structures.
    Works on both top-level data and nested company/company_info dicts."""

    def _get_prof():
        return result.setdefault("company_profile", {})

    # ── company_info dict ──
    ci = data.get("company_info", {})
    if isinstance(ci, dict) and not is_unavailable(ci.get("name_jp") or ci.get("name_ja") or ci.get("name")):
        prof = _get_prof()
        # Names
        if is_unavailable(result.get("company_name_jp")):
            result["company_name_jp"] = clean(ci.get("name_jp") or ci.get("name_ja") or ci.get("name"))
        if is_unavailable(result.get("company_name_en")):
            result["company_name_en"] = clean(ci.get("name_en"))
        # Website
        if is_unavailable(result.get("website")):
            result["website"] = clean(ci.get("website"))
        # Founded
        if is_unavailable(prof.get("founded")):
            prof["founded"] = clean(ci.get("founded"))
        # Capital
        if is_unavailable(prof.get("capital")):
            val = ci.get("capital_formatted")
            if not val:
                cap_num = ci.get("capital_jpy")
                if cap_num:
                    val = f"{cap_num:,}円" if isinstance(cap_num, (int, float)) else str(cap_num) + "円"
            prof["capital"] = clean(val)
        # Employees
        if is_unavailable(prof.get("num_of_employees")):
            emp = ci.get("employee_count")
            if emp is not None:
                prof["num_of_employees"] = str(emp) if isinstance(emp, (int, float)) else clean(emp)

    # ── headquarters ──
    hq = data.get("headquarters", {})
    if isinstance(hq, dict):
        prof = _get_prof()
        addr = clean(hq.get("address_jp") or hq.get("address_en") or hq.get("address_ja"))
        if addr and is_unavailable(prof.get("address")):
            pc = hq.get("postal_code")
            prof["address"] = f"〒{pc} {addr}" if pc else addr

    # ── contact ──
    contact = data.get("contact", {})
    if isinstance(contact, dict):
        prof = _get_prof()
        if is_unavailable(prof.get("phone")):
            prof["phone"] = clean(contact.get("tel") or contact.get("phone"))
        if is_unavailable(prof.get("fax")):
            prof["fax"] = clean(contact.get("fax"))

    # ── key_contacts (alternative structure) ──
    kc = data.get("key_contacts", {})
    if isinstance(kc, dict):
        prof = _get_prof()
        if is_unavailable(prof.get("phone")):
            prof["phone"] = clean(kc.get("phone") or kc.get("tel"))
        if is_unavailable(prof.get("fax")):
            prof["fax"] = clean(kc.get("fax"))
        hq_kc = kc.get("headquarters", {})
        if isinstance(hq_kc, dict) and is_unavailable(prof.get("address")):
            addr = clean(hq_kc.get("address_ja") or hq_kc.get("address_jp") or hq_kc.get("address_en"))
            pc = hq_kc.get("postal_code")
            if addr:
                prof["address"] = f"〒{pc} {addr}" if pc else addr

    # ── locations ──
    for loc in data.get("locations", []):
        if isinstance(loc, dict):
            prof = _get_prof()
            if is_unavailable(prof.get("address")):
                prof["address"] = clean(loc.get("address_jp") or loc.get("address_en"))
            if is_unavailable(prof.get("phone")):
                prof["phone"] = clean(loc.get("tel") or loc.get("phone"))
            if is_unavailable(prof.get("fax")):
                prof["fax"] = clean(loc.get("fax"))

    # ── business_fields ──
    domains = result.get("company_domains", [])
    for bf in data.get("business_fields", []):
        if isinstance(bf, dict):
            domain = clean(bf.get("primary_en") or bf.get("primary"))
            if domain and domain not in domains:
                domains.append(domain)
        elif isinstance(bf, str):
            d = clean(bf)
            if d and d not in domains:
                domains.append(d)
    result["company_domains"] = domains

    # ── industry_specializations ──
    for ind in data.get("industry_specializations", []):
        if isinstance(ind, dict):
            domain = clean(ind.get("industry_en") or ind.get("industry"))
            if domain and domain not in domains:
                domains.append(domain)
    result["company_domains"] = domains

    # ── technical_capabilities ──
    tech = result.get("tech_stack", [])
    tc = data.get("technical_capabilities", {})
    if isinstance(tc, dict):
        for key in ["programming_languages", "databases", "platforms", "frameworks", "cloud"]:
            for t in tc.get(key, []):
                if t and t not in tech:
                    tech.append(t)
    elif isinstance(tc, list):
        for t in tc:
            if t and t not in tech:
                tech.append(t)
    result["tech_stack"] = tech

    # ── major_clients → partners ──
    partners = result.get("partners", [])
    for client in data.get("major_clients", data.get("clients", [])):
        if isinstance(client, dict):
            name = clean(client.get("name_en") or client.get("name"))
            if name and name not in partners:
                partners.append(name)
        elif isinstance(client, str):
            name = clean(client)
            if name and name not in partners:
                partners.append(name)
    result["partners"] = partners

    # ── certifications_licenses ──
    certs = result.get("certifications", [])
    for cert in data.get("certifications_licenses", data.get("certifications", [])):
        if isinstance(cert, dict):
            name = clean(cert.get("type_en") or cert.get("type") or cert.get("name"))
            if name and name not in certs:
                certs.append(name)
        elif isinstance(cert, str):
            name = clean(cert)
            if name and name not in certs:
                certs.append(name)
    result["certifications"] = certs

    # ── affiliations ──
    for aff in data.get("affiliations", []):
        if isinstance(aff, dict):
            name = clean(aff.get("name_en") or aff.get("name"))
            if name and name not in certs:
                certs.append(name)

    # ── website link ──
    if result.get("website"):
        existing_urls = {l.get("url") for l in result.get("links", [])}
        if result["website"] not in existing_urls:
            result.setdefault("links", []).append({"name_and_description": "Website", "url": result["website"]})

    return result


# ─── Parse company-people.json ─────────────────────────────────────────────

def parse_people_json(filepath):
    """Parse company-people.json and return unified dict."""
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"  [WARN] Failed to parse {filepath}: {e}")
        return {}

    if not isinstance(data, dict):
        return {}

    result = {
        "company_name_jp": None,
        "company_name_en": None,
        "website": None,
        "people": [],
        "company_profile": {},
        "company_domains": [],
        "tech_stack": [],
        "partners": [],
        "certifications": [],
        "links": [],
    }

    # ── Schema detection ──

    # Group D: Rich schema with company_info at top level (no company wrapper)
    # e.g., Cosmic: { company_info: {...}, headquarters: {...}, executives: [...], ... }
    has_company_info = isinstance(data.get("company_info"), dict)
    has_company_dict = isinstance(data.get("company"), dict)
    has_company_name = "company_name" in data and isinstance(data.get("company_name"), str)
    has_officer_details = "officer_details" in data

    if has_company_info and not has_company_dict and not has_company_name:
        # ── Group D: company_info at top level ──
        ci = data["company_info"]
        result["company_name_jp"] = clean(ci.get("name_jp") or ci.get("name_ja") or ci.get("name"))
        result["company_name_en"] = clean(ci.get("name_en"))
        result["website"] = clean(ci.get("website"))

        # Extract all rich fields from top-level data
        extract_rich_json_fields(data, result)

        # People from "people" array
        for p in data.get("people", []):
            name = clean(p.get("name") or p.get("name_ja") or p.get("name_jp"))
            if is_unavailable(name):
                continue
            result["people"].append({
                "name_jp": name,
                "name_en": clean(p.get("name_en")),
                "title": clean(p.get("title") or p.get("title_ja") or p.get("position_jp")),
                "linkedin_url": clean(p.get("linkedin")),
                "twitter_url": clean(p.get("twitter")),
            })

        # People from "executives" array
        for e in data.get("executives", []):
            name = clean(e.get("name_jp") or e.get("name_ja") or e.get("name"))
            if is_unavailable(name):
                continue
            result["people"].append({
                "name_jp": name,
                "name_en": clean(e.get("name_en")),
                "title": clean(e.get("title_ja") or e.get("position_jp") or e.get("position_en") or e.get("role")),
                "linkedin_url": None,
                "twitter_url": None,
            })

        # People from "executive_officers"
        for e in data.get("executive_officers", []):
            name = clean(e.get("name_jp") or e.get("name_ja") or e.get("name"))
            if is_unavailable(name):
                continue
            result["people"].append({
                "name_jp": name,
                "name_en": clean(e.get("name_en")),
                "title": clean(e.get("title_ja") or e.get("title_en") or e.get("role")),
                "linkedin_url": None,
                "twitter_url": None,
            })

        # People from "advisors", "board_members"
        for key in ["advisors", "board_members"]:
            for e in data.get(key, []):
                name = clean(e.get("name_jp") or e.get("name_ja") or e.get("name"))
                if is_unavailable(name):
                    continue
                result["people"].append({
                    "name_jp": name,
                    "name_en": clean(e.get("name_en")),
                    "title": clean(e.get("title_ja") or e.get("title_en") or e.get("role")),
                    "linkedin_url": None,
                    "twitter_url": None,
                })

        # Employee count from employee_statistics
        es = data.get("employee_statistics", {})
        if isinstance(es, dict) and is_unavailable(result["company_profile"].get("num_of_employees")):
            total = es.get("total")
            if total is not None:
                result["company_profile"]["num_of_employees"] = str(total)

    # Group A: has "company" dict at top level
    elif has_company_dict:
        comp = data["company"]
        result["company_name_jp"] = clean(comp.get("name_jp") or comp.get("name_ja"))
        result["company_name_en"] = clean(comp.get("name_en"))
        result["website"] = clean(comp.get("website"))

        # Extract rich fields from top-level data
        extract_rich_json_fields(data, result)

        # People from "people" array
        for p in data.get("people", []):
            name = clean(p.get("name") or p.get("name_ja") or p.get("name_jp"))
            if is_unavailable(name):
                continue
            result["people"].append({
                "name_jp": name,
                "name_en": clean(p.get("name_en")),
                "title": clean(p.get("title") or p.get("title_ja") or p.get("position_jp")),
                "linkedin_url": clean(p.get("linkedin")),
                "twitter_url": clean(p.get("twitter")),
            })

        # People from "executives", "executive_officers", "advisors", "board_members"
        for key in ["executives", "executive_officers", "advisors", "board_members"]:
            for e in data.get(key, []):
                name = clean(e.get("name_jp") or e.get("name_ja") or e.get("name"))
                if is_unavailable(name):
                    continue
                result["people"].append({
                    "name_jp": name,
                    "name_en": clean(e.get("name_en")),
                    "title": clean(e.get("title_ja") or e.get("position_jp") or e.get("position_en") or e.get("role")),
                    "linkedin_url": None,
                    "twitter_url": None,
                })

        # Employee statistics
        es = data.get("employee_statistics", {})
        if isinstance(es, dict) and is_unavailable(result["company_profile"].get("num_of_employees")):
            total = es.get("total")
            if total is not None:
                result["company_profile"]["num_of_employees"] = str(total)

    # Group B: has "company_name" string at top level (not officer_details)
    elif has_company_name and not has_officer_details:
        result["company_name_jp"] = clean(data.get("company_name"))
        result["company_name_en"] = clean(data.get("english_name") or data.get("company_english_name"))
        result["website"] = clean(data.get("website"))

        # Extract rich fields if present
        extract_rich_json_fields(data, result)

        # People from multiple possible arrays
        people_keys = ["people", "leadership_team", "key_personnel", "contact_persons",
                       "technical_staff", "executives", "executive_officers", "board_members"]
        for key in people_keys:
            for p in data.get(key, []):
                if not isinstance(p, dict):
                    continue
                name = clean(p.get("name") or p.get("name_jp") or p.get("name_ja") or p.get("name_en"))
                if is_unavailable(name):
                    continue
                result["people"].append({
                    "name_jp": name,
                    "name_en": clean(p.get("name_en")),
                    "title": clean(p.get("title") or p.get("title_jp") or p.get("title_ja") or p.get("position_jp") or p.get("role") or p.get("designation")),
                    "linkedin_url": clean(p.get("linkedin") or p.get("linkedin_url")),
                    "twitter_url": clean(p.get("twitter") or p.get("twitter_url")),
                })

        for key in ["business_contacts", "key_people"]:
            for p in data.get(key, []):
                if not isinstance(p, dict):
                    continue
                name = clean(p.get("name") or p.get("name_jp"))
                if is_unavailable(name):
                    continue
                result["people"].append({
                    "name_jp": name,
                    "name_en": clean(p.get("name_en")),
                    "title": clean(p.get("title") or p.get("designation") or p.get("role")),
                    "linkedin_url": None,
                    "twitter_url": None,
                })

    # Group C: officer_details (placeholder schema)
    elif has_officer_details:
        result["company_name_jp"] = clean(data.get("company_name"))
        result["company_name_en"] = clean(data.get("company_english_name"))
        result["people"] = []

    return result


# ─── Parse social-profile-scraped.json ────────────────────────────────────

def parse_social_scraped(filepath):
    """Parse social-profile-scraped.json and return list of people dicts."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"  [WARN] Failed to parse {filepath}: {e}")
        return []

    people = []
    for sp in data.get("scraped_profiles", []):
        name = clean(sp.get("name"))
        if is_unavailable(name):
            continue

        linkedin_url = clean(sp.get("linkedin_url"))
        twitter_url = clean(sp.get("twitter_url"))
        linkedin_data = sp.get("linkedin_data")
        twitter_data = sp.get("twitter_data")

        linkedin_data_available = False
        if linkedin_data and isinstance(linkedin_data, dict):
            header = linkedin_data.get("header", {})
            hname = header.get("name", "")
            if hname and str(hname) != "400" and "Bad Request" not in str(header.get("headline", "")):
                linkedin_data_available = True

        twitter_data_available = twitter_data is not None and isinstance(twitter_data, dict)

        person = {
            "name_jp": name,
            "name_en": None,
            "title": clean(sp.get("role")),
            "linkedin": {
                "profile_available": linkedin_url is not None,
                "data_available": linkedin_data_available,
                "url": linkedin_url,
            },
            "twitter": {
                "profile_available": twitter_url is not None,
                "data_available": twitter_data_available,
                "url": twitter_url,
            },
        }

        if linkedin_data_available and isinstance(linkedin_data, dict):
            ld = linkedin_data
            person["linkedin"].update({
                "headline": clean(ld.get("header", {}).get("headline")),
                "location": clean(ld.get("header", {}).get("location")),
                "connections": clean(ld.get("header", {}).get("connections")),
                "about": clean(ld.get("about")),
                "experience": ld.get("experience", []),
                "education": ld.get("education", []),
                "skills": ld.get("skills", []),
                "certifications": ld.get("certifications", []),
            })
            if is_unavailable(person["title"]):
                exp_list = ld.get("experience", [])
                if exp_list and isinstance(exp_list[0], dict):
                    person["title"] = clean(exp_list[0].get("title"))

        if twitter_data_available and isinstance(twitter_data, dict):
            person["twitter"].update({
                "handle": clean(twitter_data.get("handle") or twitter_data.get("username")),
                "bio": clean(twitter_data.get("bio") or twitter_data.get("description")),
                "followers": twitter_data.get("followers_count"),
                "following": twitter_data.get("friends_count"),
            })

        people.append(person)

    return people


# ─── Parse company-info.md ───────────────────────────────────────────────

def parse_info_md(filepath):
    """Parse company-info.md and return extracted fields."""
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [WARN] Failed to read {filepath}: {e}")
        return {}

    result = {}

    # Helper: try multiple patterns, return first match
    def first_match(patterns, text, group=1):
        for pat in patterns:
            m = re.search(pat, text, re.DOTALL)
            if m:
                val = clean(m.group(group))
                if val:
                    return val
        return None

    # Helper: allow markdown between label and value
    def label_value_pattern(labels):
        """Build regex that allows **, spaces, and \n between label and value."""
        joined = "|".join(labels)
        return rf'(?:{joined})\s*[：:]*\s*(?:\*{1,2})?\s*([^\n]+)'

    # ── Company names from title ──
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        m = re.match(r'(.+?)\s*\((.+?)\)', title)
        if m:
            result.setdefault("company_name_jp", m.group(1).strip())
            result.setdefault("company_name_en", m.group(2).strip())
        else:
            result.setdefault("company_name_jp", title)

    # ── Company names from explicit fields ──
    for pat, key in [
        (r'\*\*Japanese[^*]*\*\*[：:\s]*\n?\s*(.+)', "company_name_jp"),
        (r'Japanese[：:]\s*(.+?)(?:\n|$)', "company_name_jp"),
        (r'\*\*English[^*]*\*\*[：:\s]*\n?\s*(.+)', "company_name_en"),
        (r'English[：:]\s*(.+?)(?:\n|$)', "company_name_en"),
        (r'会社名[：:]\s*(.+?)(?:\n|$)', "company_name_jp"),
    ]:
        m = re.search(pat, content)
        if m and key not in result:
            val = clean(m.group(1))
            if val:
                result[key] = val

    # ── Address ──
    postal_match = re.search(r'〒\s*(\d{3}[-ー]?\d{4})\s*(.+?)(?:\n\n|\n\*|\n#|\n\||\n-)', content, re.DOTALL)
    if postal_match:
        addr = postal_match.group(2).strip()
        addr = re.sub(r'\n(?![\n#*\-|])', '', addr)
        addr = re.sub(r'\s+', ' ', addr).strip()
        pc = postal_match.group(1)
        result["address"] = f"〒{pc} {addr}"

    for pat in [
        r'\*\*所在地\*\*[：:\s]*(.+?)(?:\n|$)',
        r'\*\*Headquarters Address\*\*[：:\s]*(.+?)(?:\n|$)',
        r'所在地[：:]\s*(.+?)(?:\n|$)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m and "address" not in result:
            addr = clean(m.group(1))
            if addr:
                result["address"] = addr

    # ── Phone (handle markdown bold) ──
    for pat in [
        r'(?:TEL|電話|Phone|Tel)\*{0,2}\s*[：:]*\s*\*{0,2}\s*([\d\-＋\(\)]+(?:\s*ext\.?\s*\d+)?)',
        r'\*\*TEL\*\*[：:\s]*(.+?)(?:\n|$)',
    ]:
        m = re.search(pat, content)
        if m:
            result["phone"] = clean(m.group(1))
            break

    # ── Fax (handle markdown bold) ──
    for pat in [
        r'(?:FAX|Fax|fax)\*{0,2}\s*[：:]*\s*\*{0,2}\s*([\d\-＋\(\)]+)',
        r'\*\*FAX\*\*[：:\s]*(.+?)(?:\n|$)',
    ]:
        m = re.search(pat, content)
        if m:
            result["fax"] = clean(m.group(1))
            break

    # ── Founded — use section-based extraction, avoid summary text ──
    # First try table rows (| Founded | value |)
    m = re.search(r'\|\s*\*?Founded\*?\s*\|\s*(.+?)\s*\|', content)
    if m:
        result["founded"] = clean(m.group(1))
    else:
        # Try section-based: look for Founded/設立 within sections, not summary
        founded = first_match([
            r'(?:^|\n)\s*[-\*]\s*\*?(?:Founded|設立|Established)\*?[：:\s]*([^\n]+)',
            r'\*{0,2}(?:Founded|設立|Established)\*{0,2}\s*[：:]\s*(\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?)',
            r'\*{0,2}(?:Founded|設立|Established)\*{0,2}\s*[：:]\s*(\d{4})\s*(?:年|[-/])',
            r'設立年月[：:\s]*([^\n]+)',
            r'(?:^|\n)\s*\|?\s*\*?(?:Founded|設立)\*?\s*[：:]*\s*(.+?)(?:\s*\|?\s*$)',
        ], content)
        if founded:
            result["founded"] = founded

    # ── Capital — avoid table milestones, look for standalone values ──
    capital = first_match([
        r'\|\s*\*?Capital\*?\s*\|\s*(.+?)\s*\|',
        r'\*{0,2}(?:Capital|資本金)\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
    ], content)
    if capital:
        # Filter out milestone-style text (e.g., "increased to 5 million yen")
        if not re.search(r'(?:increased|capital|to \d)', capital, re.IGNORECASE):
            result["capital"] = capital
        else:
            # Try to extract just the number/currency
            cm = re.search(r'([\d,]+(?:万|億|円|[¥$])[\d,]*(?:万|億|円|[¥$])*)', capital)
            if cm:
                result["capital"] = cm.group(1)

    # ── Employees — avoid summary text ──
    emp = first_match([
        r'\|\s*\*?(?:Employees|従業員数)\*?\s*\|\s*(.+?)\s*\|',
        r'\*{0,2}(?:Employees|従業員数|従業員)\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
    ], content)
    if emp:
        # Filter out summary-style text
        if not re.search(r'(?:with|company has|staff member)', emp, re.IGNORECASE):
            result["num_of_employees"] = emp
        else:
            # Try to extract just the number
            em = re.search(r'(\d+(?:\s*[-~]\s*\d+)?)', emp)
            if em:
                result["num_of_employees"] = em.group(1)

    # ── Sales / Revenue ──
    sales = []
    for pat in [
        r'\|\s*\*?(?:Revenue|売上高|Sales)\*?\s*\|\s*(.+?)\s*\|',
        r'\*{0,2}(?:Revenue|売上高|Sales)\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
    ]:
        m = re.search(pat, content)
        if m:
            val = clean(m.group(1))
            if val and not is_unavailable(val):
                sales.append({
                    "date_type": "year",
                    "date": None,
                    "total_sales": val,
                })
    if sales:
        result["sales"] = sales

    # ── Business Domains ──
    domains = []
    for pat in [
        r'\*\*Business Fields\*\*[：:\s]*(.+?)(?:\n\n|\n#|\n\*\*)',
        r'\*\*事業内容\*\*[：:\s]*(.+?)(?:\n\n|\n#|\n\*\*)',
        r'事業内容[：:\s]*(.+?)(?:\n\n|\n#|\n\*\*)',
        r'\|\s*Business Fields\s*\|\s*(.+?)\s*\n',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*(.+)', block)
            if items:
                for item in items:
                    d = clean(item)
                    if d:
                        domains.append(d)
            else:
                parts = re.split(r'[,、\n]', block)
                for p in parts:
                    d = clean(p)
                    if d:
                        domains.append(d)
            break

    if domains:
        result["company_domains"] = domains

    # ── Tech Stack ──
    tech = []
    for pat in [
        r'(?:##\s+)?\*{0,2}(?:Technology Stack|技術スタック|Technical Capabilities|技術体制|開発言語)\*{0,2}[：:\s]*\n(.+?)(?:\n\n|\n#|\n\*\*)',
        r'###\s+\*{0,2}(?:Development Languages?|開発言語|Databases?|Platforms?|データベース|プラットフォーム)\*{0,2}\s*\n(.+?)(?:\n\n|\n###)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*(.+)', block)
            if items:
                for item in items:
                    t = clean(item)
                    if t:
                        sub_parts = re.split(r'[,、]', t)
                        for sp_item in sub_parts:
                            st = clean(sp_item)
                            if st and "and others" not in st.lower() and "others" not in st.lower():
                                tech.append(st)
            break

    if not tech:
        m = re.search(r'(?:Technology Stack|技術スタック|開発言語|Development Languages?)[：:\s]*(.+?)(?:\n)', content)
        if m:
            parts = re.split(r'[,、]', m.group(1))
            for p in parts:
                t = clean(p)
                if t and "and others" not in t.lower():
                    tech.append(t)

    if tech:
        result["tech_stack"] = tech

    # ── Partners / Major Clients ──
    partners = []
    for pat in [
        r'(?:##|\*\*)\s*\*{0,2}(?:Major Business Partners?|主要取引先|Key Clients?|Clients?)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
        r'###\s+\*{0,2}Partners?\*{0,2}\s*\n(.+?)(?:\n\n|\n##|\n###)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*(.+)', block)
            if items:
                for item in items:
                    p_name = clean(item)
                    em = re.search(r'\((.+?)\)', p_name)
                    if em:
                        partners.append(clean(em.group(1)))
                    elif p_name:
                        partners.append(p_name)
            break

    if partners:
        result["partners"] = partners

    # ── Certifications ──
    certs = []
    for pat in [
        r'(?:##|\*\*)\s*\*{0,2}(?:Certifications?|許認可|資格・認定|Licensed? Certifications?)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*(.+)', block)
            if items:
                for item in items:
                    c = clean(item)
                    if c:
                        certs.append(c)
            break

    if certs:
        result["certifications"] = certs

    # ── Products and Services ──
    products = []
    for pat in [
        r'(?:##|\*\*)\s*\*{0,2}(?:Products? and Services?|製品・サービス|Products?\s*/\s*Services?)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
        r'(?:##|\*\*)\s*\*{0,2}(?:Core Business|主要事業|事業内容)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
        r'##\s+\*{0,2}Products?\*{0,2}\s*\n(.+?)(?:\n\n|\n##)',
        r'###\s+\*{0,2}Services?\*{0,2}\s*\n(.+?)(?:\n\n|\n##|\n###)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*\*{0,2}(.+?)\*{0,2}(?:\n|$)', block)
            for item in items:
                p_name = clean(item)
                if p_name and len(p_name) > 2:
                    products.append(p_name)
            break

    if products:
        result["products_and_services"] = [
            {"name": p, "type": "service", "client_type": "b2b", "description": None, "target_demography": None}
            for p in products
        ]

    # ── Links / URLs ──
    links = []
    for pat in [
        r'(?:Website|ウェブサイト)\*{0,2}[：:\s]*(https?://[^\s\n\)\]]+)',
    ]:
        m = re.search(pat, content)
        if m:
            links.append({"name_and_description": "Website", "url": clean(m.group(1))})

    all_urls = re.findall(r'(https?://[^\s\n\)\]>"]+)', content)
    for url in all_urls:
        url = clean(url)
        if url and not any(l.get("url") == url for l in links):
            links.append({"name_and_description": url, "url": url})

    if links:
        result["links"] = links

    return result


# ─── Merge people from JSON and social scrape ────────────────────────────

def normalize_name(name):
    if not name:
        return ""
    name = str(name).strip().replace(" ", "").replace("\u3000", "").replace("\u00a0", "")
    return name.lower()


def format_person_for_output(person):
    """Convert a person dict to the output schema format."""
    linkedin_url = person.get("linkedin_url")
    twitter_url = person.get("twitter_url")
    linkedin_data = person.get("linkedin_data") or {}
    twitter_data = person.get("twitter_data") or {}

    result_person = {
        "name_en": person.get("name_en"),
        "name_jp": person.get("name_jp"),
        "title": person.get("title"),
        "notes": person.get("notes"),
        "linkedin": {
            "profile_available": linkedin_url is not None,
            "data_available": linkedin_data.get("data_available", False),
            "url": linkedin_url,
        },
        "twitter": {
            "profile_available": twitter_url is not None,
            "data_available": twitter_data.get("data_available", False),
            "url": twitter_url,
        },
    }

    # Add extra LinkedIn fields if data available
    if linkedin_data.get("data_available"):
        for extra_key in ["headline", "location", "connections", "about", "experience",
                          "education", "skills", "certifications"]:
            if extra_key in linkedin_data:
                result_person["linkedin"][extra_key] = linkedin_data[extra_key]

    # Add extra Twitter fields if data available
    if twitter_data.get("data_available"):
        for extra_key in ["handle", "bio", "followers", "following"]:
            if extra_key in twitter_data:
                result_person["twitter"][extra_key] = twitter_data[extra_key]

    return result_person


def merge_people(json_people, scraped_people):
    """Merge and deduplicate people from both sources."""
    merged = []
    seen = {}

    # First pass: people from company-people.json
    for p in json_people:
        norm = normalize_name(p.get("name_jp") or p.get("name_en", ""))
        if not norm:
            continue
        # Deduplicate: if already seen, enrich existing entry
        if norm in seen:
            existing = merged[seen[norm]]
            if is_unavailable(existing.get("title")) and p.get("title"):
                existing["title"] = p.get("title")
            if not existing.get("linkedin_url") and p.get("linkedin_url"):
                existing["linkedin_url"] = p.get("linkedin_url")
            if not existing.get("twitter_url") and p.get("twitter_url"):
                existing["twitter_url"] = p.get("twitter_url")
            if is_unavailable(existing.get("name_en")) and p.get("name_en"):
                existing["name_en"] = p.get("name_en")
            continue
        entry = {
            "name_jp": p.get("name_jp"),
            "name_en": p.get("name_en"),
            "title": p.get("title"),
            "linkedin_url": p.get("linkedin_url"),
            "twitter_url": p.get("twitter_url"),
            "linkedin_data": None,
            "twitter_data": None,
        }
        seen[norm] = len(merged)
        merged.append(entry)

    # Second pass: merge scraped profiles
    for sp in scraped_people:
        norm = normalize_name(sp.get("name_jp") or sp.get("name", ""))
        if not norm:
            continue

        sp_linkedin = sp.get("linkedin", {})
        sp_twitter = sp.get("twitter", {})

        if norm in seen:
            existing = merged[seen[norm]]
            # Enrich with scraped LinkedIn data
            if sp_linkedin.get("url"):
                existing["linkedin_url"] = sp_linkedin.get("url")
                existing["linkedin_data"] = sp_linkedin
            # Enrich with scraped Twitter data
            if sp_twitter.get("url"):
                existing["twitter_url"] = sp_twitter.get("url")
                existing["twitter_data"] = sp_twitter
            # Fill title if missing
            if is_unavailable(existing.get("title")) and sp.get("title"):
                existing["title"] = sp.get("title")
        else:
            entry = {
                "name_jp": sp.get("name_jp"),
                "name_en": sp.get("name_en"),
                "title": sp.get("title"),
                "linkedin_url": sp_linkedin.get("url"),
                "twitter_url": sp_twitter.get("url"),
                "linkedin_data": sp_linkedin if sp_linkedin.get("url") else None,
                "twitter_data": sp_twitter if sp_twitter.get("url") else None,
            }
            seen[norm] = len(merged)
            merged.append(entry)

    return [format_person_for_output(p) for p in merged]


# ─── Extract company from folder ─────────────────────────────────────────

def extract_company(folder_name, folder_path):
    """Extract all data for a single company folder."""
    json_data = parse_people_json(os.path.join(folder_path, "company-people.json"))
    scraped_people = parse_social_scraped(os.path.join(folder_path, "social-profile-scraped.json"))
    md_data = parse_info_md(os.path.join(folder_path, "company-info.md"))

    # ── Company names (precedence: JSON > MD > folder name) ──
    company_name_jp = json_data.get("company_name_jp") or md_data.get("company_name_jp")
    company_name_en = json_data.get("company_name_en") or md_data.get("company_name_en")

    # ── Company profile (precedence: JSON rich > MD) ──
    jp = json_data.get("company_profile", {})
    profile = {
        "address": jp.get("address") or md_data.get("address"),
        "phone": jp.get("phone") or md_data.get("phone"),
        "fax": jp.get("fax") or md_data.get("fax"),
        "founded": jp.get("founded") or md_data.get("founded"),
        "established": md_data.get("established"),
        "capital": jp.get("capital") or md_data.get("capital"),
        "num_of_employees": jp.get("num_of_employees") or md_data.get("num_of_employees"),
        "sales": jp.get("sales") or md_data.get("sales") or [],
    }

    # ── People ──
    people = merge_people(json_data.get("people", []), scraped_people)

    # ── Other fields (precedence: JSON > MD) ──
    domains = json_data.get("company_domains") or md_data.get("company_domains") or []
    products = md_data.get("products_and_services") or []
    tech = json_data.get("tech_stack") or md_data.get("tech_stack") or []
    partners = json_data.get("partners") or md_data.get("partners") or []
    certifications = json_data.get("certifications") or md_data.get("certifications") or []

    # ── Links (combine both, deduplicate by URL) ──
    all_links = []
    seen_urls = set()
    for link_list in [json_data.get("links", []), md_data.get("links", [])]:
        for link in link_list:
            url = link.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_links.append(link)

    return {
        "company_folder_name": folder_name,
        "company_name_en": company_name_en,
        "company_name_jp": company_name_jp,
        "company_domains": domains,
        "products_and_services": products,
        "company_profile": profile,
        "people": people,
        "partners": partners,
        "certifications": certifications,
        "links": all_links,
        "tech_stack": tech,
    }


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Company Data Extraction Script")
    print("=" * 60)

    skip_names = {"company-data.json", "json-structure.md", "extract_company_data.py",
                  ".git", ".gitignore", "__pycache__"}
    folders = []
    for entry in os.listdir(ROOT_DIR):
        full_path = os.path.join(ROOT_DIR, entry)
        if os.path.isdir(full_path) and entry not in skip_names and not entry.startswith("."):
            folders.append(entry)

    folders.sort()
    print(f"\nFound {len(folders)} company folders.\n")

    companies = []
    failures = []

    for i, folder_name in enumerate(folders, 1):
        folder_path = os.path.join(ROOT_DIR, folder_name)
        try:
            company = extract_company(folder_name, folder_path)
            companies.append(company)
            if i % 50 == 0:
                print(f"  Processed {i}/{len(folders)}...")
        except Exception as e:
            failures.append((folder_name, str(e)))
            print(f"  [ERROR] Failed to process {folder_name}: {e}")
            companies.append({
                "company_folder_name": folder_name,
                "company_name_en": None,
                "company_name_jp": None,
                "company_domains": [],
                "products_and_services": [],
                "company_profile": {
                    "address": None, "phone": None, "fax": None,
                    "founded": None, "established": None, "capital": None,
                    "num_of_employees": None, "sales": [],
                },
                "people": [],
                "partners": [],
                "certifications": [],
                "links": [],
                "tech_stack": [],
            })

    print(f"\nWriting {len(companies)} companies to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    # Summary stats
    with_people = sum(1 for c in companies if c["people"])
    with_address = sum(1 for c in companies if c["company_profile"].get("address"))
    with_domains = sum(1 for c in companies if c["company_domains"])
    with_tech = sum(1 for c in companies if c["tech_stack"])
    with_partners = sum(1 for c in companies if c["partners"])
    total_people = sum(len(c["people"]) for c in companies)

    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Total companies:        {len(companies)}")
    print(f"Companies with people:  {with_people}")
    print(f"Companies with address: {with_address}")
    print(f"Companies with domains: {with_domains}")
    print(f"Companies with tech:     {with_tech}")
    print(f"Companies with partners: {with_partners}")
    print(f"Total people extracted:  {total_people}")
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for name, err in failures:
            print(f"  - {name}: {err}")
    print("=" * 60)


if __name__ == "__main__":
    main()
