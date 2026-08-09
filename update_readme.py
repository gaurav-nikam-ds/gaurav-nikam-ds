"""
update_readme.py
=================
Regenerates the sections of README.md that live between
<!-- SECTION:START --> ... <!-- SECTION:END --> markers, using
portfolio.json as the single source of truth plus live data pulled
from the GitHub API for each featured repo (description, topics,
homepage, stars).

Run locally:
    GITHUB_TOKEN=xxxx python update_readme.py

Run in Actions: see .github/workflows/update-readme.yml
"""

import json
import os
import re
import sys

import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "gaurav-nikam-ds")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {"Accept": "application/vnd.github.v3+json"}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"

README_PATH = "README.md"
CONFIG_PATH = "portfolio.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_repo_data(repo_name):
    """Pull live description / topics / homepage / stars for a repo."""
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return {
                "description": data.get("description") or "No description yet.",
                "homepage": data.get("homepage") or "",
                "topics": data.get("topics", []),
                "stars": data.get("stargazers_count", 0),
                "url": data.get("html_url", f"https://github.com/{USERNAME}/{repo_name}"),
            }
        print(f"⚠️  Could not fetch {repo_name}: HTTP {r.status_code}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"⚠️  Error fetching {repo_name}: {e}", file=sys.stderr)
    return {
        "description": "No description yet.",
        "homepage": "",
        "topics": [],
        "stars": 0,
        "url": f"https://github.com/{USERNAME}/{repo_name}",
    }


def bar(level, width=10):
    """Render a level (0-100) as a block-character progress bar."""
    filled = round((level / 100) * width)
    return "▰" * filled + "▱" * (width - filled)


def build_skills_section(skills):
    by_category = {}
    for s in skills:
        by_category.setdefault(s["category"], []).append(s)

    lines = ["<table width=\"100%\"><tr>"]
    categories = list(by_category.items())
    for i, (category, items) in enumerate(categories):
        lines.append("<td valign=\"top\" width=\"50%\">\n")
        lines.append(f"**{category}**\n")
        for s in items:
            lines.append(f"`{s['name']}` {bar(s['level'])} {s['level']}%  ")
        lines.append("\n</td>")
        if i % 2 == 1 and i != len(categories) - 1:
            lines.append("</tr><tr>")
    lines.append("</tr></table>")
    return "\n".join(lines)


def build_project_card(repo_name, override, repo_data):
    emoji = override.get("emoji", "📦")
    title = repo_name.replace("-", " ").title()
    insight = override.get("key_insight", "")
    live_url = override.get("live_url") or repo_data["homepage"]
    tags = " ".join(f"`{t}`" for t in repo_data["topics"][:5]) or "`data-analysis`"
    stars = f" · ⭐ {repo_data['stars']}" if repo_data["stars"] else ""

    live_badge = ""
    if live_url:
        live_badge = (
            f"[![Live App](https://img.shields.io/badge/▶%20LIVE%20DEMO-{title.replace(' ', '%20')}-6366F1"
            f"?style=for-the-badge&logo=streamlit&logoColor=white)]({live_url})\n"
        )

    return f"""<table>
<tr><td width="100%">

### {emoji} {title}{stars}

{repo_data['description']}

{live_badge}[![GitHub](https://img.shields.io/badge/Source-181717?style=for-the-badge&logo=github)]({repo_data['url']})

> 💡 **Key insight:** {insight}

{tags}

</td></tr>
</table>
"""


def build_projects_section(overrides):
    ordered = sorted(overrides.items(), key=lambda kv: kv[1].get("order", 999))
    cards = []
    for repo_name, override in ordered:
        repo_data = get_repo_data(repo_name)
        cards.append(build_project_card(repo_name, override, repo_data))
    return "\n".join(cards)


def build_certs_section(certs):
    header = "| Certificate | Issuer | Year |\n|:---|:---:|:---:|\n"
    rows = "\n".join(f"| {c['name']} | {c['issuer']} | {c['date']} |" for c in certs)
    return header + rows


def build_education_section(education):
    header = "| Degree | Institution | Year | Status |\n|:---|:---|:---:|:---:|\n"
    rows = "\n".join(
        f"| **{e['degree']}** | {e['institution']} | {e['year']} | {e['status']} |"
        for e in education
    )
    return header + rows


def replace_section(content, marker, new_body):
    pattern = rf"(<!-- {marker}:START -->)(.*?)(<!-- {marker}:END -->)"
    replacement = f"\\1\n{new_body}\n\\3"
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count == 0:
        print(f"⚠️  Marker '{marker}' not found in README.md — skipped.", file=sys.stderr)
        return content
    return new_content


def main():
    config = load_config()

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, "SKILLS", build_skills_section(config["skills"]))
    content = replace_section(content, "PROJECTS", build_projects_section(config["project_overrides"]))
    content = replace_section(content, "CERTS", build_certs_section(config["certifications"]))
    content = replace_section(content, "EDUCATION", build_education_section(config["education"]))

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ README.md updated from portfolio.json + live GitHub data.")


if __name__ == "__main__":
    print(f"🔄 Updating README for {USERNAME}...")
    main()
