import re
import subprocess
from bs4 import BeautifulSoup
from cohort import OBU_TEAM_ID, HSU_TEAM_ID, DSU_TEAM_ID, UWF_TEAM_ID

TEAMS = [
    ("OBU", OBU_TEAM_ID, ["M", "F"]),
    ("HSU", HSU_TEAM_ID, ["M", "F"]),
    ("DSU", DSU_TEAM_ID, ["M", "F"]),
    ("UWF", UWF_TEAM_ID, ["F"]),
]

def fetch_roster_html(team_id, gender, season_id):
    url = f"https://www.swimcloud.com/team/{team_id}/roster/?page=1&gender={gender}&season_id={season_id}&sort=name"
    print(f"  Open this URL in Safari: {url}")
    input("  Press Enter when the page is fully loaded...")
    script = 'tell application "Safari" to return (do JavaScript "document.documentElement.outerHTML" in current tab of window 1)'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  osascript error: {result.stderr.strip()}")
        return None
    return result.stdout

def parse_freshmen(html):
    soup = BeautifulSoup(html, "html.parser")
    tbody = soup.find("tbody")
    if not tbody:
        print("  Warning: no tbody found — page may have been blocked")
        return {}
    freshmen = {}
    for row in tbody.find_all("tr"):
        link = row.find("a", class_="u-text-semi")
        if not link:
            continue
        name = link.get_text(strip=True)
        match = re.search(r"/swimmer/(\d+)", link["href"])
        if not match:
            print(f"  Skipping unexpected href: {link['href']}")
            continue
        swimmer_id = int(match.group(1))
        tds = row.find_all("td")
        class_year = tds[-2].get_text(strip=True) if tds else ""
        points = tds[-1].get_text(strip=True) if tds else ""
        if class_year == "FR" and points not in ("–", "", "−"):
            freshmen[swimmer_id] = name
    return freshmen

def append_cohort_to_file(var_name, data):
    lines = [f"\n{var_name} = {{"]
    for swimmer_id, name in data.items():
        lines.append(f"    {swimmer_id}: \"{name}\",")
    lines.append("}")
    with open("cohort.py", "a") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Written {var_name} ({len(data)} swimmers)")

if __name__ == "__main__":
    season_id = input("Enter season_id to scrape (e.g. 26 for 2022-23): ").strip()
    cohort_year = input("Enter cohort year label (e.g. 2022): ").strip()

    for team_name, team_id, genders in TEAMS:
        for gender in genders:
            gender_label = "MEN" if gender == "M" else "WOMEN"
            var_name = f"{team_name}_{cohort_year}_{gender_label}"
            print(f"\nFetching {var_name}...")
            html = fetch_roster_html(team_id, gender, season_id)
            if html:
                freshmen = parse_freshmen(html)
                if freshmen:
                    append_cohort_to_file(var_name, freshmen)
                else:
                    print(f"  No freshmen found for {var_name}")

    print("\nDone.")
