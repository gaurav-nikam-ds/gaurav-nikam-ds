"""
update_readme.py
================
Auto-updates the GitHub profile README with:
- Latest project stats (stars, last updated)
- Runs via GitHub Actions daily + on every push
"""

import os
import re
import requests
from datetime import datetime, timezone

USERNAME = os.environ.get("GITHUB_USERNAME", "gaurav-nikam-ds")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

TRACKED_REPOS = [
    {
        "repo"      : "customer-churn-prediction",
        "badge"     : "PROJECT_01-📉_Customer_Churn-FF4757",
        "title"     : "Customer Churn Prediction",
        "live_link" : "https://customer-churn-prediction-7dmchid9v9vkkyigyn3ivc.streamlit.app/",
        "live_text" : "🔴 LIVE → Try it now",
        "stats_block": """```
📦 7,043 customers analyzed
🔴 1,769 flagged High Risk  
🟡 1,733 flagged Medium Risk
🟢 3,541 flagged Low Risk
```""",
        "finding"   : "Month-to-month customers churn\n> at **3× the rate** of annual holders",
        "tags"      : "`FastAPI` `Streamlit` `Logistic Regression` `scikit-learn`"
    },
    {
        "repo"      : "diabetes-prediction-app",
        "badge"     : "PROJECT_02-🩺_Diabetes_Risk-2ED573",
        "title"     : "Diabetes Risk Predictor",
        "live_link" : "https://diabetes-prediction-app-pro.streamlit.app/",
        "live_text" : "🟢 LIVE → Try it now",
        "stats_block": """```
📦 100,000 patient records
🎯 XGBoost Classifier
⚡ Real-time probability score
🔬 High / Moderate / Low risk tiers
```""",
        "finding"   : "Blood glucose alone predicts diabetes\n> better than BMI + age combined",
        "tags"      : "`XGBoost` `Streamlit` `sklearn Pipeline`"
    },
    {
        "repo"      : "SuperStore-PowerBI-Sales-Forecast",
        "badge"     : "PROJECT_03-⚡_SuperStore_BI-FFA502",
        "title"     : "SuperStore Sales Dashboard",
        "live_link" : None,
        "stats_block": """```
🔴 Tables: negative profit margin
⚠️ Discounts >20% destroy margin
🗺️ West = highest profit region
📈 Q4 seasonality pattern found
```""",
        "finding"   : "Business was losing money on Tables\n> while it appeared in revenue reports",
        "tags"      : "`Power BI` `DAX` `Python` `ETS Forecasting`"
    },
    {
        "repo"      : "Trader-Behavior-Insights",
        "badge"     : "PROJECT_04-📈_Trader_Behavior-1E90FF",
        "title"     : "Trader Behavior Insights",
        "live_link" : None,
        "stats_block": """```
🟢 Profitable traders: stable across both
🔴 Undisciplined traders: blow up in Fear
📉 High frequency + Fear = negative PnL
🧠 Discipline > market conditions
```""",
        "finding"   : "Market sentiment does NOT explain\n> why traders fail — behavior does",
        "tags"      : "`Python` `Pandas` `Seaborn` `Matplotlib`"
    },
]


def get_repo_stats(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return {
            "stars"      : data.get("stargazers_count", 0),
            "pushed_at"  : data.get("pushed_at", ""),
        }
    return {"stars": 0, "pushed_at": ""}


def build_projects_section():
    rows = []
    pairs = [(TRACKED_REPOS[i], TRACKED_REPOS[i+1] if i+1 < len(TRACKED_REPOS) else None)
             for i in range(0, len(TRACKED_REPOS), 2)]

    for left, right in pairs:
        left_cell  = build_project_cell(left)
        right_cell = build_project_cell(right) if right else "<td width='50%'></td>"
        rows.append(f"<tr>\n\n{left_cell}\n\n{right_cell}\n\n</tr>")

    return "<table>\n" + "\n".join(rows) + "\n</table>"


def build_project_cell(proj):
    if not proj:
        return "<td width='50%'></td>"

    stats    = get_repo_stats(proj["repo"])
    repo_url = f"https://github.com/{USERNAME}/{proj['repo']}"

    # Stars badge
    stars_line = ""
    if stats["stars"] > 0:
        stars_line = f"\n⭐ {stats['stars']} stars"

    # Live button or GitHub button
    if proj.get("live_link"):
        action_btn = f"**[{proj['live_text']}]({proj['live_link']})**"
        sub_text   = f"Upload data → Get predictions instantly{stars_line}"
    else:
        action_btn = f"**[View Project →]({repo_url})**"
        sub_text   = f"Analysis · Insights · Business Recommendations{stars_line}"

    return f"""<td align="center" width="50%">
<img src="https://img.shields.io/badge/{proj['badge']}?style=for-the-badge"/>

{action_btn}

{sub_text}

{proj['stats_block']}

**Key Finding:**
> {proj['finding']}

{proj['tags']}

[![GitHub](https://img.shields.io/badge/View_Code-181717?style=flat-square&logo=github)]({repo_url})

</td>"""


def update_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    projects_content = build_projects_section()
    content = re.sub(
        r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->",
        f"<!-- PROJECTS:START -->\n\n<div align=\"center\">\n\n{projects_content}\n\n</div>\n<!-- PROJECTS:END -->",
        content,
        flags=re.DOTALL
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ README.md updated!")


if __name__ == "__main__":
    print(f"🔄 Updating README for {USERNAME}...")
    update_readme()
