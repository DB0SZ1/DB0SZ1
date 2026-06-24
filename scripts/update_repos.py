import os
import re
import requests
from datetime import datetime, timezone

USERNAME = "DB0SZ1"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"} if TOKEN else {}

THEME = {
    "bg":     "f7faf7",
    "title":  "16a34a",
    "text":   "3d5c3d",
    "icon":   "16a34a",
    "border": "12",
}


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos"
    res = requests.get(url, headers=HEADERS, params={"per_page": 100, "type": "owner"})
    res.raise_for_status()
    repos = res.json()

    # exclude forks and archived repos
    repos = [r for r in repos if not r["fork"] and not r.get("archived")]

    # rank: stars first, then recency of last push
    repos.sort(
        key=lambda r: (r["stargazers_count"], r["pushed_at"]),
        reverse=True,
    )
    return repos[:3]


def pin_card_url(repo_name):
    t = THEME
    return (
        f"https://github-readme-stats.vercel.app/api/pin/"
        f"?username={USERNAME}&repo={repo_name}"
        f"&bg_color={t['bg']}&title_color={t['title']}"
        f"&text_color={t['text']}&icon_color={t['icon']}"
        f"&hide_border=true&border_radius={t['border']}"
    )


def build_section(repos):
    cards = []
    for repo in repos:
        name = repo["name"]
        url  = repo["html_url"]
        img  = pin_card_url(name)
        cards.append(
            f'<a href="{url}">\n'
            f'  <img width="32%" src="{img}"/>\n'
            f'</a>'
        )

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    joined  = "\n".join(cards)

    return (
        f'<div align="center">\n\n'
        f'{joined}\n\n'
        f'<sub>Auto-updated · {updated}</sub>\n\n'
        f'</div>'
    )


def patch_readme(section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern     = r"<!-- REPOS:START -->.*?<!-- REPOS:END -->"
    replacement = f"<!-- REPOS:START -->\n{section}\n<!-- REPOS:END -->"
    updated     = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    repos   = fetch_repos()
    section = build_section(repos)
    patch_readme(section)
    print(f"Patched README with top {len(repos)} repos:")
    for r in repos:
        print(f"  ★{r['stargazers_count']}  {r['name']}  (pushed {r['pushed_at'][:10]})")
