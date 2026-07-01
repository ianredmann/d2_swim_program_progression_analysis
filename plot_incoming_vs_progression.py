import matplotlib.pyplot as plt
from db import get_connection
from cohort import COHORTS
from analysis import top5_avg_by_season, qualifying_seasons, compute_progression

EXCLUDE = {1455202}  # Samuel Goins — converted to diving
GENDER_LABEL = {"M": "Men", "F": "Women"}

def collect_data(conn):
    points = []  # (name, gender_label, incoming_power_index, progression)

    for team, team_id, cohort_year, gender, cohort in COHORTS:
        for swimmer_id, name in cohort.items():
            if swimmer_id in EXCLUDE:
                continue

            results = top5_avg_by_season(conn, swimmer_id, team_id)
            seasons = qualifying_seasons(results)
            if len(seasons) < 3:
                continue

            cursor = conn.cursor()
            cursor.execute("SELECT incoming_power_index FROM swimmers WHERE id = ?", (swimmer_id,))
            incoming = cursor.fetchone()[0]
            if incoming is None:
                continue

            progression = compute_progression(results)
            points.append((name, GENDER_LABEL[gender], incoming, progression))

    return points

if __name__ == "__main__":
    conn = get_connection()
    points = collect_data(conn)
    conn.close()

    print(f"{len(points)} swimmers with both incoming index and 3+ year progression")

    colors = {"Men": "tab:blue", "Women": "tab:red"}
    fig, ax = plt.subplots(figsize=(9, 6))

    for gender_group in ("Men", "Women"):
        xs = [p[2] for p in points if p[1] == gender_group]
        ys = [p[3] for p in points if p[1] == gender_group]
        ax.scatter(xs, ys, c=colors[gender_group], label=gender_group, alpha=0.75, edgecolors="black", linewidths=0.5)

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Incoming power index (pre-college composite)")
    ax.set_ylabel("Progression (top-5 avg power points, freshman → final season)")
    ax.set_title("Incoming Talent vs. Progression\n(2019-2022 cohorts, OBU/HSU/DSU/UWF, 3+ year window)")
    ax.legend()
    fig.text(0.5, -0.02, "Illustrative only — small sample, not a value-added model.",
              ha="center", fontsize=8, style="italic", color="gray")
    fig.tight_layout()
    fig.savefig("incoming_vs_progression.png", dpi=150, bbox_inches="tight")
    print("Saved incoming_vs_progression.png")
