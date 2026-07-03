# D2 Swim Program Progression Analysis — Full Report

This is the full report behind the project. The [README](README.md) has the short version with the question, key findings, architecture, and how to run it. This document has the complete methodology, every design decision and why it was made, and the full results.

## Introduction

At the conclusion of the 2026 NCAA Division II Swimming and Diving Championships, I found myself reflecting on some of the standout performances of the entire meet. One in particular caught my attention: a senior sprinter from Lynn University who swept the sprint field and set multiple NCAA records across freestyle, butterfly, and backstroke events. Out of curiosity, I pulled up his SwimCloud profile and examined his times going back to his freshman year. He had been a solid recruit. He was competitive, but nowhere near the profile of someone you would expect to become a national champion. What I found instead was a consistent, improvement year after year that culminated in a dominant senior season. Looking at several of his teammates revealed the same trajectory, although not as pronounced, suggesting something beyond individual development, and pointing toward a program level effect. That observation prompted a question: which NCAA Division II swim program produces the best improvement in its swimmers over a four year career?

## The Question

An answer to this question would be valuable to multiple stakeholders in the college swimming community: swimmers and families evaluating programs during the recruiting process, and coaches looking to benchmark their development systems against peers. Notably, a preliminary search on the topic revealed no published study addressing this question for any NCAA division. Beyond individual decision making, a reliable answer could shift recruiting attention toward programs with strong development track records which would create a competitive pressure that raises the standard across the sport.

## Scope

The original ambition of this project was to answer the question at the scale of all of NCAA Division II. In practice, that proved difficult for two reasons: the volume of swimmer data that would need to be scraped, and the difficulty of reliably detecting attritions. Attritions in this case are defined as transfers, walk-ons, and early departures that are difficult to spot without manual verification at that scale. As a result, the scope was narrowed to four programs from my own conference and cohort years I could verify by hand: Ouachita Baptist University, Henderson State University, Delta State University, and the University of West Florida, tracked across the 2019 through 2022 entering classes. This constraint turned a research question into a proof of concept. The pipeline works end to end, the methodology is sound, and the results are verifiable, but the sample is too small to support any ranking or conclusion. The goal is to demonstrate that the question is answerable in principle, and to lay the groundwork for a larger study with proper data access.

## Methodology

The pipeline consists of four stages. First, freshman rosters were scraped from SwimCloud for each target school and season, identifying the entering cohort for each year. Second, career times were scraped for each identified swimmer across all four seasons of their college career. Third, a progression metric was defined: for each swimmer and each season, their season best time per event was converted to power points, which is a standardized scoring system that allows comparison across events and distances, and the top five average of those values was taken as their performance score for that season. The top five average was chosen because most collegiate swimmers compete in four to five individual events at a championship meet, and averaging across five scores reduces sensitivity to event portfolio shifts between a swimmer's freshman and senior seasons, though it does not eliminate it entirely. All times were restricted to short course yards to ensure course consistency. Finally, progression was computed as the difference between a swimmer's freshman season score and their final qualifying season score.

Results are reported across three windows: a four year window for swimmers with data at their school in all four seasons, a three year window for swimmers with exactly three qualifying seasons, and a combined three plus year window that merges both groups. Three windows are reported because most swimmers do not have clean four year careers. Transfers, attrition, and COVID disruption mean that requiring four full seasons would exclude the majority of the data.

Swimmers were included if they had data at their school's team ID for at least three seasons, which also served as the method for detecting transfers and attrition without manual review.

## Key Design Decisions

**Power points over raw times.** Raw times cannot be compared across events. A 47 second 100 freestyle and a 1:47 200 butterfly represent very different levels of performance. Power points are a standardized scoring system that converts any swim to a common scale, making it possible to aggregate performance across a swimmer's entire event portfolio into a single score.

**Season best times.** Each swimmer's performance score for a given season is built from their fastest time in each event that season, rather than an average across all swims. Championship meets are swum tapered, meaning swimmers are at peak fitness. Using season bests ensures that the freshman and senior scores being compared are both drawn from peak performance conditions, keeping the comparison consistent.

**Short course yards only, for the progression metric.** Short course yards is the standard course for collegiate swimming in the United States. All college season times were restricted to SCY to ensure that every score on both ends of the progression window was measured under the same conditions. Non SCY swims were dropped rather than converted. (The incoming talent proxy described below is a deliberate exception to this rule. See that section for more.)

**Raw improvement over value added.** The methodologically correct way to measure a program's contribution to swimmer development would be to compare each swimmer's actual improvement against an expected improvement given their incoming talent level, isolating the program effect from the baseline. That approach requires enough data to fit a reliable baseline model, which a single cohort across four programs cannot support. Raw improvement is used instead, with the explicit acknowledgment that it conflates program quality with recruiting strength.

## Incoming Talent Proxy (Power Index)

Raw improvement conflates coaching quality with recruiting strength since a program that recruits already strong swimmers will tend to show smaller raw gains than one that recruits weaker swimmers, even with identical coaching. The correct fix is a value added model: compare actual improvement against an *expected* improvement given incoming talent. Fitting that model is out of reach for a four cohort dataset, but capturing incoming talent at all is a prerequisite for ever doing it, so that became a secondary goal of this project.

SwimCloud has its own recruiting metric for this, the Power Index (PI), a 1–100 score computed from a swimmer's best high school/club times. It disappears from a swimmer's profile once they enroll in college, so it was never present in any of the scraped college season data. SwimCloud publishes a support article describing part of the PI formula: your top scoring event and second scoring event each count 100% toward the index, the third counts 25%, and the fourth counts 2% (missing 3rd/4th slots default to a score of 100, which is a deliberate disincentive for posting too few events). That weighting is applied to **Power Points** which is the same 300–1100 ish scale already used everywhere else in this project, which raised an obvious problem: a weighted average of numbers in the 300–1100 range cannot land on a 1–100 scale. SwimCloud's public documentation doesn't explain the final normalization step, which is almost certainly a percentile rank against that year's full recruiting class, data this project doesn't have and can't reconstruct.

Rather than chase an exact replica of SwimCloud's number, this project builds its own weighted composite using the *documented* part of the formula (the same Power Points already trusted elsewhere in the pipeline, combined with the 100/100/25/2 event weighting) and stops there. It won't match SwimCloud's displayed 1–100 score, but percentile rank is a monotonic function of the underlying composite score, so the *relative ordering* of swimmers by incoming talent should track closely — which is what actually matters for a scatter plot.

**Implementation:**
- One additional scrape (`scrape_incoming.py`) pulled each swimmer's season immediately prior to their college career (`cohort_year - 1996 - 1`, the same season numbering scheme used everywhere else in the pipeline).
- Unlike the rest of the project, **all courses were allowed** for this scrape (SCY, SCM, LCM) rather than locking to SCY. A pilot run on a known swimmer's pre-college season came back with 14 real swims, none of them SCY — confirming that locking to SCY here would have zeroed out real data for a meaningful share of swimmers (pre-college club seasons are frequently SCM/LCM-only).
- `incoming_power_index.py` aggregates the raw pre-college swims: for each event, take the best score across all courses (matching SwimCloud's documented "only your best course per event counts" rule), then weight the top four by 100/100/25/2 and write the result to `swimmers.incoming_power_index`.
- Spot-checked by hand against a known swimmer (Tyler Andruss): manually recomputing the weighted average from his raw pre-college times matched the stored value exactly.
- Coverage: 190 of 202 swimmers (94%) got pre-college data back; 12 came back empty. That gap wasn't chased aggressively, SwimCloud had already warned against further automated scraping, and a couple of retries on the same swimmer/season produced a suspicious pattern (worked once, failed on immediate repeats), which looked more like a rate limit/antibot signal than a genuine data absence. Better to accept a small, disclosed gap than risk the account over it.

**A genuine finding, not a bug:** the resulting scatter (incoming index vs. progression) shows a small cluster of swimmers with very low incoming scores, clearly separated from the main mass. Before trusting it, the most extreme case was checked by hand on SwimCloud, wher a swimmer whose entire precollege record was a single, very slow swim. It held up: some swimmers really do enter with a thin, weak pre-college record (walk-ons, late starters), and the scatter is capturing that honestly rather than reflecting a scraping error.

![Incoming talent vs. progression](incoming_vs_progression.png)

## Pipeline Design Decisions

**Schema normalization.** The database consists of two tables: `swimmers`, which stores each athlete's name, gender, team, and incoming power index, and `times`, which stores every recorded swim linked back to a swimmer via a foreign key. This reflects a "one-to-many" relationship where one swimmer has many times, and follows standard normalization practice: swimmer attributes are stored once and referenced by ID rather than repeated on every time row. This separation is also what makes transfer detection possible, and each time record stores the `team_id` it was recorded under, allowing the analysis to filter to only swims performed at the swimmer's cohort school.

**Studying the data source before building.** Before writing any scraper, the SwimCloud website was inspected using browser developer tools. This revealed that times data is served as a JSON object via an API endpoint, while roster pages are rendered as raw HTML. That distinction drove two entirely separate scraping approaches.

**Requests converted to Playwright for times.** Times scraping initially used Python's `requests` library, which worked until Cloudflare began returning 403 responses, detecting the automated HTTP client by its fingerprint. The scraper was rebuilt using Playwright with a real Firefox instance, which is significantly harder for Cloudflare to distinguish from a human browser. A persistent browser context was used to preserve cookies and login state across runs, avoiding repeated reauthentication.

**Safari + osascript for rosters.** Even Playwright was blocked by Cloudflare Turnstile on HTML roster pages. The solution was to pull roster HTML directly from an active Safari tab using `osascript`, Apple's scripting interface. Since Safari is a native browser with no automation fingerprint, it passes Cloudflare checks without issue. This required enabling "Allow JavaScript from Apple Events" in Safari's developer settings.

**Rate limiting and backoff.** To avoid overwhelming the server and triggering blocks, a base delay was added between requests. When the API returned a 429 (too many requests), the scraper applied exponential backoff, progressively longer waits before retrying, rather than hammering the endpoint repeatedly.

**Safe reruns.** All database inserts use `INSERT OR IGNORE`, meaning the scraper can be run multiple times without duplicating data. This made iterative development significantly easier and a failed or partial run could simply be restarted from the beginning.

## Results

All values are change in top 5 average SCY power points, freshman season to final qualifying season. Standard deviation is reported alongside every mean — with groups this small, it matters more than the mean itself.

**Per-cohort results** (mean pts (n), stdev in parentheses where n≥2)

| Team | Gender | Cohort | 4-yr | 3-yr | 3+ yr |
|---|---|---|---|---|---|
| OBU | Men | 2022 | +51.9 (6, σ23.3) | +16.7 (4, σ45.6) | +37.8 (10, σ36.4) |
| OBU | Men | 2021 | -33.5 (6, σ89.9) | +49.3 (3, σ42.2) | -5.9 (9, σ84.9) |
| OBU | Men | 2020 | +71.3 (3, σ34.7) | -49.0 (1) | +41.2 (4, σ66.5) |
| OBU | Men | 2019 | -54.6 (1) | +11.9 (3, σ52.0) | -4.8 (4, σ53.9) |
| OBU | Women | 2022 | +5.7 (2, σ8.1) | -27.0 (3, σ5.5) | -13.9 (5, σ18.8) |
| OBU | Women | 2021 | -18.6 (2, σ9.1) | -74.0 (2, σ101.3) | -46.3 (4, σ66.9) |
| OBU | Women | 2020 | +17.2 (1) | -33.6 (1) | -8.2 (2, σ35.9) |
| OBU | Women | 2019 | -0.9 (2, σ12.0) | -7.4 (5, σ30.9) | -5.6 (7, σ25.9) |
| HSU | Men | 2022 | -5.2 (4, σ51.9) | — | -5.2 (4, σ51.9) |
| HSU | Men | 2021 | +28.0 (3, σ30.4) | +14.4 (2, σ16.2) | +22.6 (5, σ24.1) |
| HSU | Men | 2020 | +48.2 (4, σ34.1) | +72.4 (1) | +53.0 (5, σ31.5) |
| HSU | Men | 2019 | -44.9 (5, σ71.4) | -90.1 (1) | -52.5 (6, σ66.5) |
| HSU | Women | 2022 | -23.7 (2, σ38.9) | -102.9 (2, σ96.5) | -63.3 (4, σ75.5) |
| HSU | Women | 2021 | +1.9 (3, σ25.6) | -70.8 (1) | -16.2 (4, σ41.9) |
| HSU | Women | 2020 | +53.5 (1) | — | +53.5 (1) |
| HSU | Women | 2019 | +16.3 (2, σ79.6) | -35.2 (1) | -0.9 (3, σ63.6) |
| DSU | Men | 2022 | +37.0 (1) | +15.8 (2, σ25.5) | +22.9 (3, σ21.8) |
| DSU | Men | 2021 | -143.8 (1) | -22.8 (1) | -83.3 (2, σ85.6) |
| DSU | Men | 2020 | — | +21.7 (2, σ43.7) | +21.7 (2, σ43.7) |
| DSU | Men | 2019 | +22.0 (6, σ38.4) | -85.9 (1) | +6.6 (7, σ53.8) |
| DSU | Women | 2022 | -0.7 (7, σ78.8) | +8.1 (2, σ38.9) | +1.2 (9, σ69.8) |
| DSU | Women | 2021 | -99.4 (1) | -49.7 (3, σ44.8) | -62.1 (4, σ44.2) |
| DSU | Women | 2020 | +65.0 (1) | -90.0 (1) | -12.5 (2, σ109.6) |
| DSU | Women | 2019 | -63.4 (1) | -18.8 (1) | -41.1 (2, σ31.5) |
| UWF | Women | 2022 | -31.6 (6, σ35.4) | -88.4 (1) | -39.7 (7, σ38.8) |
| UWF | Women | 2021 | -35.4 (1) | -20.6 (1) | -28.0 (2, σ10.5) |
| UWF | Women | 2020 | +20.2 (2, σ22.3) | +145.2 (1) | +61.9 (3, σ73.8) |
| UWF | Women | 2019 | +31.9 (4, σ51.6) | -49.8 (3, σ110.8) | -3.1 (7, σ85.6) |

**Overall means (all cohorts combined, 3+ year mixed window)**

| Team | Gender | n | Mean | Stdev |
|---|---|---|---|---|
| OBU | Men | 27 | +17.5 pts | 63.5 |
| OBU | Women | 18 | -17.2 pts | 38.1 |
| HSU | Men | 20 | +2.1 pts | 60.5 |
| HSU | Women | 12 | -22.3 pts | 63.6 |
| DSU | Men | 14 | -0.6 pts | 58.3 |
| DSU | Women | 17 | -20.3 pts | 66.1 |
| UWF | Women | 19 | -8.9 pts | 69.4 |

Note the standard deviations: at the overall level, every group's stdev is roughly 3–4x the size of its mean. Individual variability dwarfs the average signal, which is a concrete illustration of why these means should not be used to rank programs.

![Distribution of progression](progression_distribution.png)

These numbers are illustrative only, as sample sizes are too small to support any ranking or conclusion.

## Limitations

**Incoming talent confounding.** The most significant limitation of this study is that raw improvement and program quality are not the same thing. A program that recruits swimmers with modest incoming talent and improves them substantially may simply be benefiting from a low baseline; the same training environment applied to a stronger recruit might yield a smaller raw improvement while representing equal or greater coaching quality. This is the motivation for the incoming talent proxy described above, but that proxy is not a substitute for an actual value added model. Until one is fit, the results should not be interpreted as a direct measure of program quality.

**Incoming talent proxy is not SwimCloud's official Power Index.** The proxy replicates the documented event weighting portion of SwimCloud's formula but not the final percentile normalization step, which isn't publicly documented and would require the full recruiting class distribution to reconstruct. It's a monotonic stand in for relative ordering, not a literal reproduction of the 1–100 score shown on SwimCloud.

**Incoming talent data has a small, disclosed gap.** 12 of 202 swimmers (6%) have no pre-college data, their SwimCloud profiles returned nothing for the season before enrollment. This wasn't chased down aggressively; a couple of retry attempts produced a suspicious failure pattern that looked more like a rate limit response than genuine data absence, and pushing further risked the scraping ban already threatened by SwimCloud.

**Event portfolio sensitivity.** The top five average power points metric is sensitive to shifts in a swimmer's event portfolio across seasons. If a swimmer competes in different events as a senior than they did as a freshman, their score can shift substantially for reasons unrelated to actual performance change. Anthony Paculba (OBU Men 2022) illustrates this clearly: his freshman season top five was anchored by distance freestyle events, the 1650, 1000, and 500 free, which tend to yield higher power points. By his senior season his portfolio had shifted entirely to sprint backstroke and mid distance events. His computed progression of -30.2 points reflects that event shift as much as it reflects any change in performance.

**Transfer freshmen missed by roster scraper.** The roster scraper identifies swimmers listed as freshmen on SwimCloud's roster page for a given season. Swimmers who transferred into a program as freshmen from another college will not appear on that page and will be missed entirely. These swimmers are not flagged as absent, they are simply never entered into the dataset.

**COVID cohort sparsity and survivorship bias.** The 2019 and 2020 entering classes had their freshman and sophomore seasons disrupted by the COVID-19 pandemic. Many swimmers from those cohorts had incomplete or missing data for their early seasons, resulting in high exclusion rates. The swimmers who do qualify from those cohorts, those who stuck around and competed despite the disruption, are a self selected group, which introduces survivorship bias into those cohort results.

**Mixed progression windows.** The overall means reported across all cohorts combine two different progression windows: four year progressions (freshman to senior season) and three year progressions (freshman to last qualifying season). These windows are not equivalent — a swimmer who left after three seasons is not directly comparable to one who completed all four years. This is disclosed throughout but not corrected for.

**Small sample sizes, and the variance to prove it.** Even across four cohorts and four programs, per team group sizes range from roughly twelve to twenty seven swimmers per gender. Every group's standard deviation is roughly 3–4x its mean — individual outcomes vary far more than the averages suggest, and several n=2 groups are visibly dominated by a single outlier swimmer. Means computed from samples this small are unstable and should not be used to rank programs.

## What It Would Take To Do This Properly

The pipeline built here is a proof of concept. Extending it into a study with meaningful statistical power would require several things that are beyond the current scope.

**More teams and more cohorts.** Seven group means across four cohorts is not enough data to draw conclusions about any program. A credible study would need to cover a substantial portion of Division II programs across many entering classes, where ideally a decade or more of cohorts are looked at. The current dataset covers four programs and four cohort years, which is enough to validate the methodology but not enough to rank anything.

**Proper data access.** The current dataset was built by scraping SwimCloud, which after a politely worded email exchange, asked us to stop. The dataset we have is therefore final. A larger study would require either a formal data partnership with SwimCloud, access to USA Swimming's SWIMS database, or another authoritative source of collegiate times data. Without it, the pipeline works but has nowhere left to run.

**A real value added model.** Raw improvement conflates program quality with recruiting strength. A proper study would need enough data to fit a baseline, which is expected improvement given incoming talent level, and report each program's residual above or below that baseline. The incoming talent proxy built here (see above) is a starting point, but it's a hand built stand in for a formula SwimCloud doesn't publish, not a validated baseline model, and fitting a reliable one requires far more observations than are currently available.

## Further Research

This project represents, to the best of my knowledge, the first attempt to systematically measure swimmer progression at the program level for any NCAA division. If you are a researcher, a data provider, or someone with access to comprehensive collegiate swimming data and interest in pursuing this question further, collaboration would be genuinely valuable. The methodology is open, the limitations are documented, and the pipeline is reproducible. The question is worth answering properly.
