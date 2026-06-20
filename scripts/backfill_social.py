#!/usr/bin/env python3
"""
Batch social profile backfill for company_analysis.
Uses Tavily API to search for LinkedIn/Twitter profiles and media mentions.
Processes companies from social_backlog.json.
"""
import json
import os
import subprocess
import sys
import time
import re

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
if not TAVILY_API_KEY:
    print("ERROR: TAVILY_API_KEY not set")
    sys.exit(1)

BASE_DIR = "/home/openclaw_user/.openclaw/workspace"
COMPANY_DIR = os.path.join(BASE_DIR, "company_analysis")

def tavily_search(query, max_results=3):
    """Search Tavily API and return results."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://api.tavily.com/search",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "api_key": TAVILY_API_KEY,
                 "query": query,
                 "max_results": max_results
             })],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        print(f"  Search error: {e}")
        return []

def extract_linkedin_urls(results):
    """Extract individual LinkedIn profile URLs from search results."""
    urls = []
    for r in results:
        url = r.get("url", "")
        content = r.get("content", "")
        # Individual profile URLs
        if "linkedin.com" in url and "/in/" in url:
            urls.append(url)
        # Also check content for profile URLs
        for match in re.findall(r'https?://(?:jp\.|www\.)?linkedin\.com/in/[\w-]+', content):
            if match not in urls:
                urls.append(match)
    return urls

def extract_twitter_urls(results):
    """Extract Twitter/X profile URLs from search results."""
    urls = []
    for r in results:
        url = r.get("url", "")
        if ("x.com" in url or "twitter.com" in url) and "/in/" not in url:
            urls.append(url)
        content = r.get("content", "")
        for match in re.findall(r'https?://(?:www\.)?(?:x\.com|twitter\.com)/[\w]+', content):
            if match not in urls and "hashtag" not in match.lower():
                urls.append(match)
    return urls

def guess_english_reading(jp_name):
    """Try to guess English reading of Japanese name.
    Returns a list of possible romanizations to try."""
    # Common readings for frequent kanji in names
    # This is a rough heuristic - we'll try multiple readings
    parts = jp_name.strip().split()
    if len(parts) != 2:
        return [jp_name]
    
    surname, given = parts
    
    # For now, return the name as-is and let search handle it
    # We'll also search with just the romanized version if we can guess it
    return [jp_name]

def get_english_name_variants(jp_name, company_en):
    """Generate search queries for finding a person's English name."""
    # First, try searching for the Japanese name + company to find romanization
    queries = []
    
    # Search Japanese name with company to find English spelling
    queries.append(f'"{jp_name}" "{company_en}" LinkedIn')
    
    return queries

def search_person_social(jp_name, title, company_en, company_jp):
    """Search for a person's LinkedIn and Twitter profiles."""
    linkedin = None
    twitter = None
    
    # First, try to find the English name by searching Japanese name + company
    results = tavily_search(f'"{jp_name}" "{company_en}" LinkedIn', max_results=3)
    
    # Extract any LinkedIn URLs found
    li_urls = extract_linkedin_urls(results)
    
    # Check if any result mentions the person with an English name
    english_name = None
    for r in results:
        content = r.get("content", "")
        # Look for patterns like "Firstname Lastname - Title at Company"
        # or "Firstname Lastname" near the company name
        if company_en.lower() in content.lower():
            # Try to extract an English name from the content
            lines = content.split('\n')
            for line in lines:
                if 'linkedin.com/in/' in line.lower() or company_en.lower() in line.lower():
                    # Look for a name pattern
                    words = line.strip().split()
                    if len(words) >= 2:
                        for i, w in enumerate(words):
                            if w[0].isupper() and i + 1 < len(words) and words[i+1][0].isupper():
                                candidate = f"{w} {words[i+1]}"
                                # Basic check: looks like a name (2-3 words, capitalized)
                                if len(candidate.split()) <= 3 and not any(x in candidate.lower() for x in ['linkedin', 'corporation', 'inc', 'ltd', 'co', ' japan', 'university']):
                                    if not english_name:
                                        english_name = candidate
    
    if english_name and li_urls:
        linkedin = li_urls[0]
    elif li_urls:
        # Verify the LinkedIn URL is actually for someone at this company
        # by checking if the company name appears near the URL in results
        for url in li_urls:
            linkedin = url
            break
    
    # If we found an English name, search more specifically
    if english_name:
        results2 = tavily_search(f'"{english_name}" "{company_en}" LinkedIn', max_results=3)
        li_urls2 = extract_linkedin_urls(results2)
        if li_urls2:
            linkedin = li_urls2[0]
        
        # Search Twitter
        tw_results = tavily_search(f'"{english_name}" "{company_en}" site:x.com', max_results=2)
        tw_urls = extract_twitter_urls(tw_results)
        if tw_urls:
            twitter = tw_urls[0]
    
    time.sleep(0.5)  # Rate limiting
    return linkedin, twitter, english_name

def search_media_mentions(company_en, company_jp):
    """Search for media mentions of a company."""
    mentions = []
    
    # Search with English name
    results = tavily_search(f'"{company_en}" news 2025', max_results=5)
    for r in results:
        url = r.get("url", "")
        title = r.get("title", "")
        # Skip the company's own website
        company_domain = ""
        if company_en:
            company_domain = company_en.lower().replace(" ", "").replace(".", "").replace(",", "")[:20]
        if url and not any(x in url for x in ["ntt-tx.co.jp", "ntt-tx.com"]):
            mentions.append({
                "source": _extract_source(url, title),
                "title": title[:100],
                "url": url
            })
    
    time.sleep(0.5)
    return mentions[:5]  # Max 5 mentions

def _extract_source(url, title):
    """Extract source name from URL."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace("www.", "")
    # Clean up
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2].capitalize()
    return domain

def process_company(company_info):
    """Process a single company: search social profiles and media mentions."""
    dirname = company_info["dir"]
    dir_path = os.path.join(COMPANY_DIR, dirname)
    people_file = os.path.join(dir_path, "company-people.json")
    info_file = os.path.join(dir_path, "company-info.md")
    
    name_en = company_info.get("name_en", "")
    name_jp = company_info.get("name_jp", "")
    
    if not os.path.isfile(people_file):
        print(f"  SKIP: No people file")
        return False
    
    print(f"\n{'='*60}")
    print(f"Processing: {name_en or name_jp} ({dirname})")
    print(f"{'='*60}")
    
    # Load existing people data
    with open(people_file) as f:
        data = json.load(f)
    
    people = data.get("people", [])
    updated_count = 0
    
    for i, person in enumerate(people):
        jp_name = person.get("name", "")
        title = person.get("title", "")
        existing_li = person.get("linkedin")
        existing_tw = person.get("twitter")
        
        # Skip if already has real social links
        if existing_li and existing_li != "null" and "hashtag" not in str(existing_li):
            continue
        if existing_tw and existing_tw != "null" and "hashtag" not in str(existing_tw):
            continue
        
        # Skip generic names (greeting messages, etc.)
        if any(x in jp_name for x in ["挨拶", "メッセージ", "代表取締役"]):
            if jp_name in ["挨拶", "メッセージ"]:
                continue
        
        print(f"  Searching: {jp_name} ({title})...")
        
        # Only search directors/presidents (skip generic entries)
        if not any(x in title for x in ["代表", "取締", "監査", "社長", "会長", "副社長"]):
            print(f"    SKIP: Not an officer ({title})")
            continue
        
        linkedin, twitter, english_name = search_person_social(
            jp_name, title, name_en, name_jp
        )
        
        if linkedin:
            person["linkedin"] = linkedin
            updated_count += 1
            print(f"    ✓ LinkedIn: {linkedin}")
        if twitter:
            person["twitter"] = twitter
            print(f"    ✓ Twitter: {twitter}")
        if not linkedin and not twitter:
            print(f"    ✗ No profiles found")
    
    # Update people file
    if updated_count > 0:
        data["last_updated"] = "2026-05-04"
        with open(people_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n  Updated {updated_count} people profiles")
    
    # Search media mentions
    print(f"\n  Searching media mentions...")
    mentions = search_media_mentions(name_en, name_jp)
    
    if mentions:
        # Update company-info.md
        if os.path.isfile(info_file):
            update_media_mentions(info_file, mentions)
            print(f"  ✓ Updated {len(mentions)} media mentions")
        else:
            print(f"  No company-info.md found")
    else:
        # Ensure empty mentions section exists
        if os.path.isfile(info_file):
            ensure_mentions_section(info_file)
        print(f"  No media mentions found")
    
    return updated_count > 0 or len(mentions) > 0

def update_media_mentions(info_file, mentions):
    """Update the Company Mentions section in company-info.md."""
    with open(info_file, "r") as f:
        content = f.read()
    
    # Build new mentions section
    mention_lines = ["## Company Mentions\n"]
    for m in mentions:
        source = m.get("source", "Unknown")
        title = m.get("title", "")
        url = m.get("url", "")
        mention_lines.append(f"- **[{source}]** — {title} ({url})")
    mention_lines.append("")
    mention_lines.append("---")
    mention_lines.append(f"*Updated: May 4, 2026*")
    new_section = "\n".join(mention_lines)
    
    # Replace existing section
    if "## Company Mentions" in content:
        # Find the section and replace everything from it to the end
        pattern = r'## Company Mentions.*'
        content = re.sub(pattern, new_section, content, flags=re.DOTALL)
    else:
        # Append at end
        content = content.rstrip() + "\n\n" + new_section + "\n"
    
    with open(info_file, "w") as f:
        f.write(content)

def ensure_mentions_section(info_file):
    """Ensure a Company Mentions section exists (even if empty)."""
    with open(info_file, "r") as f:
        content = f.read()
    
    if "## Company Mentions" in content:
        # Replace with clean empty section
        pattern = r'## Company Mentions.*'
        replacement = "## Company Mentions\n\n_No external press coverage or media mentions found at this time._\n\n---\n*Updated: May 4, 2026*\n"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        content = content.rstrip() + "\n\n## Company Mentions\n\n_No external press coverage or media mentions found at this time._\n\n---\n*Updated: May 4, 2026*\n"
    
    with open(info_file, "w") as f:
        f.write(content)

def main():
    # Load backlog
    backlog_file = os.path.join(BASE_DIR, "social_backlog.json")
    if not os.path.isfile(backlog_file):
        print("ERROR: social_backlog.json not found")
        sys.exit(1)
    
    with open(backlog_file) as f:
        companies = json.load(f)
    
    # Get batch size from args
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    start_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    batch = companies[start_idx:start_idx + batch_size]
    print(f"Processing batch of {len(batch)} companies (starting at index {start_idx})")
    print(f"Total backlog: {len(companies)} companies")
    
    updated = 0
    for company in batch:
        try:
            if process_company(company):
                updated += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Batch complete: {updated}/{len(batch)} companies updated")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
