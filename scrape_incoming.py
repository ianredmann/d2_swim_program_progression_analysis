import time
from playwright.sync_api import sync_playwright
from db import get_connection
from cohort import COHORTS
from scraper import fetch_times, insert_swimmer

def insert_incoming_times(conn, swimmer_id, times):
    for t in times:
        if t["pointvalue"] is None:
            continue
        if t["relay_id"] is not None and t["legposition"] != 1:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO times (id, swimmer_id, season_id, team_id, event_distance, event_stroke, event_course, event_time, point_value, date_of_swim) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (t["id"], swimmer_id, t["season_id"], t["team_id"], t["eventdistance"], t["eventstroke"], t["eventcourse"], t["eventtime"], t["pointvalue"], t["dateofswim"])
        )
    conn.commit()

if __name__ == "__main__":
    import sys
    target_year = int(sys.argv[1]) if len(sys.argv) > 1 else None
    cohorts_to_run = [c for c in COHORTS if target_year is None or c[2] == target_year]

    conn = get_connection()

    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            user_data_dir="./browser_data_firefox",
            headless=False,
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.goto("https://www.swimcloud.com")
        input("Log into SwimCloud in the browser window, then press Enter here to start scraping...")

        for team, team_id, cohort_year, gender, cohort in cohorts_to_run:
            pre_college_season = cohort_year - 1996 - 1
            for swimmer_id, name in cohort.items():
                insert_swimmer(conn, swimmer_id, name, gender, team, cohort_year)
                print(f"Fetching {name}, pre-college season {pre_college_season}...")
                times = fetch_times(page, swimmer_id, pre_college_season)
                insert_incoming_times(conn, swimmer_id, times)
                time.sleep(2)

        context.close()

    conn.close()
    print("Done.")
