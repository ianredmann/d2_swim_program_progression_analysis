import matplotlib.pyplot as plt
from db import get_connection
from cohort import COHORTS
from analysis import top5_avg_by_season, qualifying_seasons, compute_progression

EXCLUDE = {1455202}  # Samuel Goins — converted to diving
GENDER_LABEL = {"M": "Men", "F": "Women"}

def collect_progressions(conn):
    by_gender = {"Men": [], "Women": []}

    for team, team_id, cohort_year, gender, cohort in COHORTS:
        for swimmer_id, name in cohort.items():
            if swimmer_id in EXCLUDE:
                continue
            results = top5_avg_by_season(conn, swimmer_id, team_id)
            seasons = qualifying_seasons(results)
            if len(seasons) < 3:
                continue
            progression = compute_progression(results)
            by_gender[GENDER_LABEL[gender]].append(progression)

    return by_gender

if __name__ == "__main__":
    conn = get_connection()
    by_gender = collect_progressions(conn)
    conn.close()

    total = len(by_gender["Men"]) + len(by_gender["Women"])
    print(f"{total} swimmers ({len(by_gender['Men'])} men, {len(by_gender['Women'])} women)")

    colors = {"Men": "tab:blue", "Women": "tab:red"}
    fig, ax = plt.subplots(figsize=(9, 6))

    bins = 20
    ax.hist([by_gender["Men"], by_gender["Women"]],
            bins=bins, stacked=True,
            color=[colors["Men"], colors["Women"]],
            label=["Men", "Women"],
            edgecolor="black", linewidth=0.5)

    ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Progression (top-5 avg power points, freshman → final season)")
    ax.set_ylabel("Number of swimmers")
    ax.set_title("Distribution of Progression\n(2019-2022 cohorts, OBU/HSU/DSU/UWF, 3+ year window)")
    ax.legend()
    fig.text(0.5, -0.02, "Illustrative only — small sample.", ha="center", fontsize=8, style="italic", color="gray")
    fig.tight_layout()
    fig.savefig("progression_distribution.png", dpi=150, bbox_inches="tight")
    print("Saved progression_distribution.png")
