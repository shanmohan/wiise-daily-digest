#!/usr/bin/env python3
"""
Daily AI & Agentic Tech Digest Generator
Uses Anthropic API with web search to curate news and generate a print-friendly HTML page.
Runs via GitHub Actions on a daily cron schedule.
"""

import anthropic
import json
import re
from datetime import datetime, timezone

def get_today():
    """Get today's date in various formats."""
    now = datetime.now(timezone.utc)
    return {
        "iso": now.strftime("%Y-%m-%d"),
        "long": now.strftime("%A, %B %d, %Y"),
        "short": now.strftime("%B %d, %Y"),
    }

def generate_digest():
    client = anthropic.Anthropic()
    today = get_today()

    prompt = f"""Today is {today['long']}. You are generating a daily AI & Agentic Tech news digest for a CTO.

Search the web for today's latest news across these categories:
1. Agentic AI & Frameworks (LangChain, CrewAI, AutoGen, Claude Agent SDK, OpenAI Agents, Google ADK, etc.)
2. Developer Tools & Capabilities (Claude Code, Cursor, GitHub Copilot, Windsurf, Codex, IDEs)
3. Enterprise & Products (Google, Microsoft, Anthropic, OpenAI, Meta, AWS, Salesforce announcements)
4. Benchmarks & Research (model releases, benchmark comparisons, research breakthroughs)
5. Industry Trends & Analysis (WSJ, Bloomberg, TechCrunch, VentureBeat, regulation, policy)

Search at least 5-6 different queries to get broad coverage. Find 15-20 distinct articles.

Then output ONLY a complete, valid HTML document (no markdown, no explanation) with:
- DOCTYPE html, UTF-8, title "AI & Agentic Tech Daily Digest — {today['long']}"
- Embedded print-optimized CSS: Georgia/serif font, 11pt, 1.6 line-height, 2cm padding
- @media print: page-break-inside:avoid on articles, page-break-before:always on h2 (except first), hide .url class, show href after links
- @media screen: max-width 800px centered, dark blue links
- Masthead: "AI & Agentic Tech Daily Digest" with date "{today['long']}"
- Table of contents with 5 section links
- 5 sections (h2), each with 3-4 articles containing: h3 title, italic source line, 2-3 sentence summary paragraph, URL in a div.url
- Footer: "Curated for Wiise CTO — Daily Briefing | Generated {today['long']}"
- Each article summary must be your own words — never copy from sources

Output ONLY the HTML. No ```html markers. Start with <!DOCTYPE html>."""

    # Use Claude with web search
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 10,
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract the HTML from the response
    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    # Clean up — ensure it starts with <!DOCTYPE
    if "<!DOCTYPE" in html_content:
        html_content = html_content[html_content.index("<!DOCTYPE"):]
    if "</html>" in html_content:
        html_content = html_content[:html_content.index("</html>") + len("</html>")]

    return html_content

def update_index(today):
    """Update index.html with the new digest entry."""
    index_path = "index.html"

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    digest_filename = f"daily-digest-{today['iso']}.html"
    new_latest_link = f'<a href="{digest_filename}">Read Today\'s Digest &rarr;</a>'
    new_latest_date = f'<div class="date">{today["long"]}</div>'

    # Update latest digest link
    index_html = re.sub(
        r'<a href="daily-digest-[^"]+\.html">Read Today\'s Digest &rarr;</a>',
        new_latest_link,
        index_html
    )
    index_html = re.sub(
        r'<div class="date">[^<]+</div>',
        new_latest_date,
        index_html,
        count=1
    )

    # Add new archive entry at top of list
    new_entry = f'        <li><a href="{digest_filename}">{today["short"]}</a> — 20 articles across 5 categories</li>\n'
    index_html = index_html.replace(
        '<ul class="archive-list">\n',
        f'<ul class="archive-list">\n{new_entry}'
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)

def main():
    today = get_today()
    digest_filename = f"daily-digest-{today['iso']}.html"

    print(f"Generating digest for {today['long']}...")
    html_content = generate_digest()

    # Write the digest file
    with open(digest_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Written: {digest_filename} ({len(html_content)} bytes)")

    # Update index.html
    update_index(today)
    print("Updated: index.html")

    print("Done!")

if __name__ == "__main__":
    main()
