#!/usr/bin/env python3
"""
Extract company data from ~306 folders into a single company-data.json file.
Reads company-info.md, company-people.json, social-profiles.md, and social-profile-scraped.json.
Uses domain_mapping.json for normalized domain names.
"""

import json
import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(ROOT_DIR, "company-data.json")
DOMAIN_MAP_FILE = os.path.join(ROOT_DIR, "domain_mapping.json")

SKIP_DIRS = {"__pycache__", "openspec", ".git", ".claude"}

UNAVAILABLE = {"Not available", "N/A", "n/a", "—", "-", "住所情報が必要",
               "年月情報が必要", "人数情報が必要", "代表者情報が必要", "Research Required",
               "[Research Required]", "情報が必要", "unknown", "Unknown", ""}


def load_domain_map():
    with open(DOMAIN_MAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


DOMAIN_MAP = load_domain_map()


def is_unavailable(val):
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() in UNAVAILABLE or val.strip().startswith("Not available")
    return False


def clean(val):
    if is_unavailable(val):
        return None
    if isinstance(val, str):
        val = val.strip()
        val = re.sub(r'\*\*', '', val)
        return val if val else None
    return val


def normalize_domains(raw_domains):
    """Map raw Japanese domain strings to normalized English names."""
    normalized = []
    seen = set()
    for raw in raw_domains:
        raw = raw.strip()
        if not raw:
            continue
        # Direct lookup
        if raw in DOMAIN_MAP:
            mapped = DOMAIN_MAP[raw]
        else:
            # Try partial matching
            mapped = None
            for key, val in DOMAIN_MAP.items():
                if key in raw:
                    mapped = val
                    break
            if not mapped:
                # Keep original if no match
                mapped = raw
        if mapped not in seen:
            seen.add(mapped)
            normalized.append(mapped)
    return normalized


# ─── Parse company-info.md ───────────────────────────────────────────────

def parse_info_md(filepath):
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {}

    result = {}

    def first_match(patterns, group=1):
        for pat in patterns:
            m = re.search(pat, content, re.DOTALL)
            if m:
                val = clean(m.group(group))
                if val:
                    return val
        return None

    # Title → names
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # Try "Japanese | English" format
        m = re.match(r'(.+?)\s*\|\s*(.+)', title)
        if m:
            result.setdefault("company_name_jp", m.group(1).strip())
            result.setdefault("company_name_en", m.group(2).strip())
        else:
            m2 = re.match(r'(.+?)\s*\((.+?)\)', title)
            if m2:
                result.setdefault("company_name_jp", m2.group(1).strip())
                result.setdefault("company_name_en", m2.group(2).strip())
            else:
                result.setdefault("company_name_jp", title)

    # Explicit name fields
    for pat, key in [
        (r'\*\*Name\*\*[：:\s]*(.+)', "company_name_jp"),
        (r'\*\*Japanese Name\*\*[：:\s]*(.+)', "company_name_jp"),
        (r'\*\*English Name\*\*[：:\s]*(.+)', "company_name_en"),
        (r'-\s*\*\*Name\*\*[：:\s]*(.+)', "company_name_jp"),
        (r'-\s*\*\*English Name\*\*[：:\s]*(.+)', "company_name_en"),
    ]:
        m = re.search(pat, content)
        if m and key not in result:
            val = clean(m.group(1))
            if val:
                result[key] = val

    # Website
    for pat in [
        r'\*\*Website\*\*[：:\s]*(https?://[^\s\n\)\]]+)',
        r'-\s*\*\*Website\*\*[：:\s]*(https?://[^\s\n\)\]]+)',
        r'(?:Website|ウェブサイト)[：:\s]*(https?://[^\s\n\)\]]+)',
    ]:
        m = re.search(pat, content)
        if m:
            result["website"] = clean(m.group(1))
            break

    # Address
    postal_match = re.search(r'〒\s*(\d{3}[-ー]?\d{4})\s*(.+?)(?:\n\n|\n\*|\n#|\n\||\n-)', content, re.DOTALL)
    if postal_match:
        addr = postal_match.group(2).strip()
        addr = re.sub(r'\n(?![\n#*\-|])', '', addr)
        addr = re.sub(r'\s+', ' ', addr).strip()
        pc = postal_match.group(1)
        result["address"] = f"〒{pc} {addr}"

    if "address" not in result:
        for pat in [
            r'\*\*所在地\*\*[：:\s]*(.+?)(?:\n|$)',
            r'\*\*Headquarters Address\*\*[：:\s]*(.+?)(?:\n|$)',
            r'\*\*Address\*\*[：:\s]*(.+?)(?:\n|$)',
            r'-\s*\*\*Address\*\*[：:\s]*(.+?)(?:\n|$)',
            r'-\s*\*\*所在地\*\*[：:\s]*(.+?)(?:\n|$)',
            r'所在地[：:]\s*(.+?)(?:\n|$)',
        ]:
            m = re.search(pat, content, re.DOTALL)
            if m:
                addr = clean(m.group(1))
                if addr:
                    result["address"] = addr
                    break

    # Phone
    for pat in [
        r'(?:TEL|電話|Phone|Tel)\*{0,2}\s*[：:]*\s*\*{0,2}\s*([\d\-＋\(\)]+(?:\s*ext\.?\s*\d+)?)',
        r'-\s*\*\*TEL\*\*[：:\s]*([\d\-＋\(\)]+)',
        r'-\s*\*\*Phone\*\*[：:\s]*([\d\-＋\(\)]+)',
    ]:
        m = re.search(pat, content)
        if m:
            result["phone"] = clean(m.group(1))
            break

    # Fax
    for pat in [
        r'(?:FAX|Fax|fax)\*{0,2}\s*[：:]*\s*\*{0,2}\s*([\d\-＋\(\)]+)',
        r'-\s*\*\*FAX\*\*[：:\s]*([\d\-＋\(\)]+)',
    ]:
        m = re.search(pat, content)
        if m:
            result["fax"] = clean(m.group(1))
            break

    # Founded
    founded = first_match([
        r'\|\s*\*?Founded\*?\s*\|\s*(.+?)\s*\|',
        r'(?:^|\n)\s*[-\*]\s*\*?(?:Founded|設立|Established)\*?[：:\s]*([^\n]+)',
        r'\*{0,2}(?:Founded|設立|Established)\*{0,2}\s*[：:]\s*(\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?)',
        r'\*{0,2}(?:Founded|設立|Established)\*{0,2}\s*[：:]\s*(\d{4})\s*(?:年|[-/])',
        r'設立年月[：:\s]*([^\n]+)',
        r'-\s*\*\*Founded\*\*[：:\s]*([^\n]+)',
    ])
    if founded:
        result["founded"] = founded

    # Capital
    capital = first_match([
        r'\|\s*\*?Capital\*?\s*\|\s*(.+?)\s*\|',
        r'\*{0,2}(?:Capital|資本金)\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
        r'-\s*\*\*(?:Capital|資本金)\*\*[：:\s]*(.+?)(?:\n|$)',
    ])
    if capital:
        cm = re.search(r'([\d,]+(?:万|億|円|[¥$])[\d,]*(?:万|億|円|[¥$])*)', capital)
        if cm:
            result["capital"] = cm.group(1)
        elif not re.search(r'(?:increased|to \d)', capital, re.IGNORECASE):
            result["capital"] = capital

    # Employees
    emp = first_match([
        r'\|\s*\*?(?:Employees|従業員数)\*?\s*\|\s*(.+?)\s*\|',
        r'\*{0,2}(?:Employees|従業員数|従業員)\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
        r'-\s*\*\*(?:Employees|従業員数|従業員)\*\*[：:\s]*(.+?)(?:\n|$)',
    ])
    if emp:
        em = re.search(r'(\d+(?:\s*[-~]\s*\d+)?)', emp)
        if em:
            result["num_of_employees"] = em.group(1)

    # Sales/Revenue
    sales = []
    for pat in [
        r'\|\s*\*?(?:Revenue|売上高|Sales)\*?\s*\|\s*(.+?)\s*\|',
        r'\*{0,2}(?:Revenue|売上高|Sales)\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
        r'-\s*\*\*(?:Revenue|売上高|Sales)\*\*[：:\s]*(.+?)(?:\n|$)',
    ]:
        m = re.search(pat, content)
        if m:
            val = clean(m.group(1))
            if val and not is_unavailable(val):
                sales.append({"date_type": "year", "date": None, "total_sales": val})
    if sales:
        result["sales"] = sales

    # Business Fields → domains
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
        result["company_domains_raw"] = domains

    # Tech Stack
    tech = []
    for pat in [
        r'(?:##\s+)?\*{0,2}(?:Technology Stack|技術スタック|Technical Capabilities|開発言語)\*{0,2}[：:\s]*\n(.+?)(?:\n\n|\n#|\n\*\*)',
        r'###\s+\*{0,2}(?:Development Languages?|開発言語|Databases?|データベース)\*{0,2}\s*\n(.+?)(?:\n\n|\n###)',
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
                            if st and "and others" not in st.lower():
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

    # Partners
    partners = []
    for pat in [
        r'(?:##|\*\*)\s*\*{0,2}(?:Major Business Partners?|主要取引先|Key Clients?)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
        r'###\s+\*{0,2}Partners?\*{0,2}\s*\n(.+?)(?:\n\n|\n##|\n###)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*(.+)', block)
            for item in items:
                p_name = clean(item)
                if p_name:
                    partners.append(p_name)
            break

    if partners:
        result["partners"] = partners

    # Certifications
    certs = []
    for pat in [
        r'(?:##|\*\*)\s*\*{0,2}(?:Certifications?|許認可|資格・認定)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
    ]:
        m = re.search(pat, content, re.DOTALL)
        if m:
            block = m.group(1)
            items = re.findall(r'[-•]\s*(.+)', block)
            for item in items:
                c = clean(item)
                if c:
                    certs.append(c)
            break

    if certs:
        result["certifications"] = certs

    # Products and Services
    products = []
    for pat in [
        r'(?:##|\*\*)\s*\*{0,2}(?:Products? and Services?|製品・サービス)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
        r'(?:##|\*\*)\s*\*{0,2}(?:Core Business|主要事業|事業内容)\*{0,2}\s*(?:##|\*\*)?\s*\n(.+?)(?:\n\n|\n##|\n###)',
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

    # Links
    links = []
    seen_urls = set()
    all_urls = re.findall(r'(https?://[^\s\n\)\]>"]+)', content)
    for url in all_urls:
        url = clean(url)
        if url and url not in seen_urls:
            seen_urls.add(url)
            links.append({"name_and_description": url, "url": url})

    if links:
        result["links"] = links

    return result


# ─── Parse company-people.json ─────────────────────────────────────────────

def parse_people_json(filepath):
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
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
        "company_domains_raw": [],
        "tech_stack": [],
        "partners": [],
        "certifications": [],
        "links": [],
    }

    # Schema detection
    has_company_dict = isinstance(data.get("company"), dict)
    has_company_info = isinstance(data.get("company_info"), dict)
    has_company_name = "company_name" in data and isinstance(data.get("company_name"), str)

    def extract_people_from_arrays(data_dict):
        """Extract people from various array keys."""
        people = []
        for key in ["people", "executives", "executive_officers", "advisors",
                     "board_members", "leadership_team", "key_personnel", "officers"]:
            for p in data_dict.get(key, []):
                if not isinstance(p, dict):
                    continue
                name = clean(p.get("name") or p.get("name_jp") or p.get("name_ja"))
                if is_unavailable(name):
                    continue
                people.append({
                    "name_jp": name,
                    "name_en": clean(p.get("name_en")),
                    "title": clean(p.get("title") or p.get("title_ja") or p.get("position_jp") or p.get("role")),
                    "linkedin_url": clean(p.get("linkedin") or p.get("linkedin_url")),
                    "twitter_url": clean(p.get("twitter") or p.get("twitter_url")),
                    "notes": clean(p.get("notes")),
                })
        return people

    if has_company_dict:
        comp = data["company"]
        result["company_name_jp"] = clean(comp.get("name_jp") or comp.get("name_ja"))
        result["company_name_en"] = clean(comp.get("name_en"))
        result["website"] = clean(comp.get("website"))
        result["people"] = extract_people_from_arrays(data)
    elif has_company_info:
        ci = data["company_info"]
        result["company_name_jp"] = clean(ci.get("name_jp") or ci.get("name_ja") or ci.get("name"))
        result["company_name_en"] = clean(ci.get("name_en"))
        result["website"] = clean(ci.get("website"))
        result["people"] = extract_people_from_arrays(data)

        # Rich fields from top-level
        prof = result.setdefault("company_profile", {})
        if is_unavailable(prof.get("founded")):
            prof["founded"] = clean(ci.get("founded"))
        if is_unavailable(prof.get("capital")):
            val = ci.get("capital_formatted")
            if not val:
                cap_num = ci.get("capital_jpy")
                if cap_num:
                    val = f"{cap_num:,}円" if isinstance(cap_num, (int, float)) else str(cap_num) + "円"
            prof["capital"] = clean(val)

        # Headquarters
        hq = data.get("headquarters", {})
        if isinstance(hq, dict):
            addr = clean(hq.get("address_jp") or hq.get("address_en") or hq.get("address_ja"))
            if addr:
                pc = hq.get("postal_code")
                prof["address"] = f"〒{pc} {addr}" if pc else addr

        # Contact
        contact = data.get("contact", {})
        if isinstance(contact, dict):
            prof["phone"] = clean(contact.get("tel") or contact.get("phone"))
            prof["fax"] = clean(contact.get("fax"))

        # Employee count
        es = data.get("employee_statistics", {})
        if isinstance(es, dict):
            total = es.get("total")
            if total is not None:
                prof["num_of_employees"] = str(total)

        # Business fields → domains
        for bf in data.get("business_fields", []):
            if isinstance(bf, dict):
                domain = clean(bf.get("primary_en") or bf.get("primary"))
                if domain:
                    result["company_domains_raw"].append(domain)
            elif isinstance(bf, str):
                d = clean(bf)
                if d:
                    result["company_domains_raw"].append(d)

        # Tech stack
        tech = []
        tc = data.get("technical_capabilities", {})
        if isinstance(tc, dict):
            for key in ["programming_languages", "databases", "platforms", "frameworks", "cloud"]:
                for t in tc.get(key, []):
                    if t and t not in tech:
                        tech.append(t)
        result["tech_stack"] = tech

        # Partners
        partners = []
        for client in data.get("major_clients", data.get("clients", [])):
            if isinstance(client, dict):
                name = clean(client.get("name_en") or client.get("name"))
                if name:
                    partners.append(name)
            elif isinstance(client, str):
                name = clean(client)
                if name:
                    partners.append(name)
        result["partners"] = partners

        # Certifications
        certs = []
        for cert in data.get("certifications_licenses", data.get("certifications", [])):
            if isinstance(cert, dict):
                name = clean(cert.get("type_en") or cert.get("type") or cert.get("name"))
                if name:
                    certs.append(name)
            elif isinstance(cert, str):
                name = clean(cert)
                if name:
                    certs.append(name)
        result["certifications"] = certs

    elif has_company_name:
        result["company_name_jp"] = clean(data.get("company_name"))
        result["company_name_en"] = clean(data.get("english_name") or data.get("company_english_name"))
        result["website"] = clean(data.get("website"))
        result["people"] = extract_people_from_arrays(data)

    # Officer details (placeholder schema)
    if "officer_details" in data and not result["people"]:
        result["people"] = []

    return result


# ─── Parse social-profile-scraped.json ────────────────────────────────────

def parse_social_scraped(filepath):
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
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


# ─── Merge people from JSON and social scrape ────────────────────────────

def normalize_name(name):
    if not name:
        return ""
    return str(name).strip().replace(" ", "").replace("\u3000", "").replace("\u00a0", "").lower()


def merge_people(json_people, scraped_people):
    merged = []
    seen = {}

    for p in json_people:
        norm = normalize_name(p.get("name_jp") or p.get("name_en", ""))
        if not norm:
            continue
        if norm in seen:
            existing = merged[seen[norm]]
            if is_unavailable(existing.get("title")) and p.get("title"):
                existing["title"] = p.get("title")
            if not existing.get("linkedin_url") and p.get("linkedin_url"):
                existing["linkedin_url"] = p.get("linkedin_url")
            if not existing.get("twitter_url") and p.get("twitter_url"):
                existing["twitter_url"] = p.get("twitter_url")
            continue
        entry = {
            "name_jp": p.get("name_jp"),
            "name_en": p.get("name_en"),
            "title": p.get("title"),
            "notes": p.get("notes"),
            "linkedin_url": p.get("linkedin_url"),
            "twitter_url": p.get("twitter_url"),
            "linkedin_data": None,
            "twitter_data": None,
        }
        seen[norm] = len(merged)
        merged.append(entry)

    for sp in scraped_people:
        norm = normalize_name(sp.get("name_jp") or "")
        if not norm:
            continue
        sp_linkedin = sp.get("linkedin", {})
        sp_twitter = sp.get("twitter", {})

        if norm in seen:
            existing = merged[seen[norm]]
            if sp_linkedin.get("url"):
                existing["linkedin_url"] = sp_linkedin.get("url")
                existing["linkedin_data"] = sp_linkedin
            if sp_twitter.get("url"):
                existing["twitter_url"] = sp_twitter.get("url")
                existing["twitter_data"] = sp_twitter
            if is_unavailable(existing.get("title")) and sp.get("title"):
                existing["title"] = sp.get("title")
            if is_unavailable(existing.get("name_en")):
                # Try to get English name from LinkedIn header
                if sp_linkedin.get("headline"):
                    pass  # too unreliable
        else:
            entry = {
                "name_jp": sp.get("name_jp"),
                "name_en": sp.get("name_en"),
                "title": sp.get("title"),
                "notes": None,
                "linkedin_url": sp_linkedin.get("url"),
                "twitter_url": sp_twitter.get("url"),
                "linkedin_data": sp_linkedin if sp_linkedin.get("url") else None,
                "twitter_data": sp_twitter if sp_twitter.get("url") else None,
            }
            seen[norm] = len(merged)
            merged.append(entry)

    return [format_person(p) for p in merged]


def format_person(person):
    linkedin_url = person.get("linkedin_url")
    twitter_url = person.get("twitter_url")
    linkedin_data = person.get("linkedin_data") or {}
    twitter_data = person.get("twitter_data") or {}

    result = {
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

    if linkedin_data.get("data_available"):
        for key in ["headline", "location", "connections", "about", "experience",
                     "education", "skills", "certifications"]:
            if key in linkedin_data:
                result["linkedin"][key] = linkedin_data[key]

    if twitter_data.get("data_available"):
        for key in ["handle", "bio", "followers", "following"]:
            if key in twitter_data:
                result["twitter"][key] = twitter_data[key]

    return result


# ─── Extract company from folder ─────────────────────────────────────────

def extract_company(folder_name, folder_path):
    json_data = parse_people_json(os.path.join(folder_path, "company-people.json"))
    scraped_people = parse_social_scraped(os.path.join(folder_path, "social-profile-scraped.json"))
    md_data = parse_info_md(os.path.join(folder_path, "company-info.md"))

    # Company names (JSON > MD)
    company_name_jp = json_data.get("company_name_jp") or md_data.get("company_name_jp")
    company_name_en = json_data.get("company_name_en") or md_data.get("company_name_en")

    # Company profile
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

    # People
    people = merge_people(json_data.get("people", []), scraped_people)

    # Domains - combine from both sources, normalize
    raw_domains = json_data.get("company_domains_raw", []) + md_data.get("company_domains_raw", [])
    domains = normalize_domains(raw_domains)

    # Other fields
    products = md_data.get("products_and_services") or []
    tech = json_data.get("tech_stack") or md_data.get("tech_stack") or []
    partners = json_data.get("partners") or md_data.get("partners") or []
    certifications = json_data.get("certifications") or md_data.get("certifications") or []

    # Links (deduplicate)
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

    folders = []
    for entry in sorted(os.listdir(ROOT_DIR)):
        full_path = os.path.join(ROOT_DIR, entry)
        if os.path.isdir(full_path) and entry not in SKIP_DIRS and not entry.startswith("."):
            folders.append(entry)

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
            print(f"  [ERROR] {folder_name}: {e}")
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

    # Summary
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
    print(f"Companies with tech:    {with_tech}")
    print(f"Companies with partners:{with_partners}")
    print(f"Total people extracted:  {total_people}")
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for name, err in failures:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
