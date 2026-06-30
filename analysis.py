from db import get_connection

def top5_avg_by_season(conn, swimmer_id, team_id):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT season_id, AVG(point_value)
        FROM times t1
        WHERE swimmer_id = ?
        AND team_id = ?
        AND (
            SELECT COUNT(*) FROM times t2
            WHERE t2.swimmer_id = t1.swimmer_id
            AND t2.season_id = t1.season_id
            AND t2.team_id = t1.team_id
            AND t2.point_value > t1.point_value
        ) < 5
        GROUP BY season_id""",
        (swimmer_id, team_id,)
    )
    return cursor.fetchall()

def qualifying_seasons(results):
    return sorted(row[0] for row in results)

def compute_progression(results):
    season_map = {row[0]: row[1] for row in results}
    seasons = qualifying_seasons(results)
    return season_map[seasons[-1]] - season_map[seasons[0]]

if __name__ == "__main__":
    from cohort import COHORTS
    conn = get_connection()

    EXCLUDE = {1455202}  # Samuel Goins — converted to diving

    gender_label = {"M": "Men", "F": "Women"}

    groups = [(team_name, cohort_year, gender_label[gender], cohort, team_id) for team_name, team_id, cohort_year, gender, cohort in COHORTS]

    overall = {}  # key: (team_name, group_name), value: list of (name, prog)

    for team_name, cohort_year, group_name, cohort, cohort_team_id in groups:
        four_year = []
        three_year = []
        excluded = []

        for swimmer_id, name in cohort.items():
            if swimmer_id in EXCLUDE:
                excluded.append((name, "excluded"))
                continue
            results = top5_avg_by_season(conn, swimmer_id, cohort_team_id)
            seasons = qualifying_seasons(results)
            if len(seasons) == 4:
                four_year.append((name, compute_progression(results)))
            elif len(seasons) == 3:
                three_year.append((name, compute_progression(results)))
            else:
                excluded.append((name, f"insufficient data (n={len(seasons)})"))

        print(f"\n--- {team_name} {cohort_year} {group_name} | 4-year ---")
        for name, prog in four_year:
            print(f"  {name}: {prog:+.1f} pts")
        if four_year:
            mean = sum(p for _, p in four_year) / len(four_year)
            print(f"  Group mean: {mean:+.1f} pts (n={len(four_year)})")

        print(f"\n--- {team_name} {cohort_year} {group_name} | 3-year ---")
        for name, prog in three_year:
            print(f"  {name}: {prog:+.1f} pts")
        if three_year:
            mean = sum(p for _, p in three_year) / len(three_year)
            print(f"  Group mean: {mean:+.1f} pts (n={len(three_year)})")

        combined = four_year + three_year
        print(f"\n--- {team_name} {cohort_year} {group_name} | 3+ year (combined, mixed window) ---")
        for name, prog in combined:
            print(f"  {name}: {prog:+.1f} pts")
        if combined:
            mean = sum(p for _, p in combined) / len(combined)
            print(f"  Group mean: {mean:+.1f} pts (n={len(combined)})")

        if excluded:
            print(f"\n  Excluded/insufficient:")
            for name, reason in excluded:
                print(f"    {name}: {reason}")

        key = (team_name, group_name)
        if key not in overall:
            overall[key] = []
        overall[key].extend(combined)

    print("\n" + "=" * 50)
    print("OVERALL (all cohorts combined, 3+ year mixed window)")
    print("=" * 50)
    for (team_name, group_name), results in overall.items():
        if results:
            mean = sum(p for _, p in results) / len(results)
            print(f"  {team_name} {group_name}: {mean:+.1f} pts (n={len(results)})")

    conn.close()



