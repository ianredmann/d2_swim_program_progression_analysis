from db import get_connection
from cohort import COHORTS

WEIGHTS = [1.0, 1.0, 0.25, 0.02]  # event 1, 2, 3, 4
DEFAULT_SCORE = 100  # used for missing 3rd/4th events, per SwimCloud's documented formula
WEIGHT_SUM = sum(WEIGHTS)

def best_event_scores(conn, swimmer_id, season_id):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT event_distance, event_stroke, MAX(point_value)
        FROM times
        WHERE swimmer_id = ? AND season_id = ?
        GROUP BY event_distance, event_stroke""",
        (swimmer_id, season_id)
    )
    return [row[2] for row in cursor.fetchall()]

def compute_incoming_power_index(conn, swimmer_id, season_id):
    scores = best_event_scores(conn, swimmer_id, season_id)
    if not scores:
        return None
    scores.sort(reverse=True)
    top_four = scores[:4] + [DEFAULT_SCORE] * (4 - len(scores[:4]))
    weighted_sum = sum(score * weight for score, weight in zip(top_four, WEIGHTS))
    return weighted_sum / WEIGHT_SUM

if __name__ == "__main__":
    conn = get_connection()
    updated = 0
    skipped = []

    for team, team_id, cohort_year, gender, cohort in COHORTS:
        pre_college_season = cohort_year - 1996 - 1
        for swimmer_id, name in cohort.items():
            power_index = compute_incoming_power_index(conn, swimmer_id, pre_college_season)
            if power_index is None:
                skipped.append(name)
                continue
            conn.execute(
                "UPDATE swimmers SET incoming_power_index = ? WHERE id = ?",
                (power_index, swimmer_id)
            )
            updated += 1

    conn.commit()
    conn.close()

    print(f"Updated {updated} swimmers.")
    print(f"Skipped {len(skipped)} (no pre-college data):")
    for name in skipped:
        print(f"  {name}")
