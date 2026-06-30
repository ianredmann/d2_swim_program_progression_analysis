# D2 Swim Program Progression Analysis

## Introduction

At the conclusion of the 2026 NCAA Division II Swimming and Diving Championships, I found myself reflecting on some of the standout performances of the entire meet. One in particular caught my attention: a senior sprinter from Lynn University who swept the sprint field and set multiple NCAA records across freestyle, butterfly, and backstroke events. Out of curiosity, I pulled up his SwimCloud profile and examined his times going back to his freshman year. He had been a solid recruit. He was competitive, but nowhere near the profile of someone you would expect to become a national champion. What I found instead was a consistent, improvement year after year that culminated in a dominant senior season. Looking at several of his teammates revealed the same trajectory, although not as pronounced, suggesting something beyond individual development, and pointing toward a program-level effect. That observation prompted a question: which NCAA Division II swim program produces the best improvement in its swimmers over a four-year career?

## The Question

An answer to this question would be valuable to multiple stakeholders in the college swimming community: swimmers and families evaluating programs during the recruiting process, and coaches looking to benchmark their development systems against peers. Notably, a preliminary search on the topic revealed no published study addressing this question for any NCAA division. Beyond individual decision making, a reliable answer could shift recruiting attention toward programs with strong development track records which would create a competitive pressure that raises the standard across the sport.

## Scope

The original ambition of this project was to answer the question at the scale of all of NCAA Division II. In practice, that proved difficult for two reasons: the volume of swimmer data that would need to be scraped, and the difficulty of reliably detecting attritions. Attritions in this case are defined as transfers, walk-ons, and early departures that are difficult to spot without manual verification at that scale. As a result, the scope was narrowed to four programs from my own conference and cohort years I could verify by hand: Ouachita Baptist University, Henderson State University, Delta State University, and the University of West Florida, tracked across the 2019 through 2022 entering classes. This constraint turned a research question into a proof of concept. The pipeline works end to end, the methodology is sound, and the results are verifiable, but the sample is too small to support any ranking or conclusion. The goal is to demonstrate that the question is answerable in principle, and to lay the groundwork for a larger study with proper data access.

## Methodology

The pipeline consists of four stages. First, freshman rosters were scraped from SwimCloud for each target school and season, identifying the entering cohort for each year. Second, career times were scraped for each identified swimmer across all four seasons of their college career. Third, a progression metric was defined: for each swimmer and each season, their season best time per event was converted to power points, which is a standardized scoring system that allows comparison across events and distances, and the top five average of those values was taken as their performance score for that season. The top five average was chosen because most collegiate swimmers compete in four to five individual events at a championship meet, and averaging across five scores reduces sensitivity to event portfolio shifts between a swimmer's freshman and senior seasons, though it does not eliminate it entirely. All times were restricted to short course yards to ensure course consistency. Finally, progression was computed as the difference between a swimmer's freshman season score and their final qualifying season score.

Results are reported across three windows: a four-year window for swimmers with data at their school in all four seasons, a three-year window for swimmers with exactly three qualifying seasons, and a combined three plus year window that merges both groups. Three windows are reported because most swimmers do not have clean four year careers. Transfers, attrition, and COVID disruption mean that requiring four full seasons would exclude the majority of the data.

Swimmers were included if they had data at their school's team ID for at least three seasons, which also served as the method for detecting transfers and attrition without manual review.

## Key Design Decisions

**Power points over raw times.** Raw times cannot be compared across events. A 47 second 100 freestyle and a 1:47 200 butterfly represent very different levels of performance. Power points are a standardized scoring system that converts any swim to a common scale, making it possible to aggregate performance across a swimmer's entire event portfolio into a single score.

**Season-best times.** Each swimmer's performance score for a given season is built from their fastest time in each event that season, rather than an average across all swims. Championship meets are swum tapered, meaning swimmers are at peak fitness. Using season bests ensures that the freshman and senior scores being compared are both drawn from peak-performance conditions, keeping the comparison consistent.

**Short-course yards only.** Short course yards is the standard course for collegiate swimming in the United States. All times were restricted to SCY to ensure that every score on both ends of the progression window was measured under the same conditions. Non SCY swims were dropped rather than converted.

**Raw improvement over value added.** The methodologically correct way to measure a program's contribution to swimmer development would be to compare each swimmer's actual improvement against an expected improvement given their incoming talent level, isolating the program effect from the baseline. That approach requires enough data to fit a reliable baseline model, which a single cohort across four programs cannot support. Raw improvement is used instead, with the explicit acknowledgment that it conflates program quality with recruiting strength. Incoming power index scores were recorded at scrape time so that a value added model can be layered in when the scope expands.

## Pipeline Design Decisions

**Schema normalization.** The database consists of two tables: `swimmers`, which stores each athlete's name, gender, team, and incoming power index, and `times`, which stores every recorded swim linked back to a swimmer via a foreign key. This reflects a "one-to-many" relationship where one swimmer has many times, and follows standard normalization practice: swimmer attributes are stored once and referenced by ID rather than repeated on every time row. This separation is also what makes transfer detection possible, and each time record stores the `team_id` it was recorded under, allowing the analysis to filter to only swims performed at the swimmer's cohort school.

**Studying the data source before building.** Before writing any scraper, the SwimCloud website was inspected using browser developer tools. This revealed that times data is served as a JSON object via an API endpoint, while roster pages are rendered as raw HTML. That distinction drove two entirely separate scraping approaches.

**Requests converted to Playwright for times.** Times scraping initially used Python's `requests` library, which worked until Cloudflare began returning 403 responses, detecting the automated HTTP client by its fingerprint. The scraper was rebuilt using Playwright with a real Firefox instance, which is significantly harder for Cloudflare to distinguish from a human browser. A persistent browser context was used to preserve cookies and login state across runs, avoiding repeated reauthentication.

**Safari + osascript for rosters.** Even Playwright was blocked by Cloudflare Turnstile on HTML roster pages. The solution was to pull roster HTML directly from an active Safari tab using `osascript`, Apple's scripting interface. Since Safari is a native browser with no automation fingerprint, it passes Cloudflare checks without issue. This required enabling "Allow JavaScript from Apple Events" in Safari's developer settings.

**Rate limiting and backoff.** To avoid overwhelming the server and triggering blocks, a base delay was added between requests. When the API returned a 429 (too many requests), the scraper applied exponential backoff, progressively longer waits before retrying,  rather than hammering the endpoint repeatedly.

**Safe reruns.** All database inserts use `INSERT OR IGNORE`, meaning the scraper can be run multiple times without duplicating data. This made iterative development significantly easier and a failed or partial run could simply be restarted from the beginning.

## Limitations

**Incoming talent confounding.** The most significant limitation of this study is that raw improvement and program quality are not the same thing. A program that recruits swimmers with modest incoming talent and improves them substantially may simply be benefiting from a low baseline, the same training environment applied to a stronger recruit might yield a smaller raw improvement while representing equal or greater coaching quality. The methodologically correct approach would be to compare each swimmer's actual improvement against an expected improvement given their incoming talent level, isolating the program effect from the baseline. This is known as a value added model, and it requires enough data to fit a reliable baseline, something a four cohort, four team dataset cannot support. Incoming power index scores were captured during scraping so that this model can be layered in when the scope expands. Until then, the results should not be interpreted as a direct measure of program quality.

**Event portfolio sensitivity.** The top five average power points metric is sensitive to shifts in a swimmer's event portfolio across seasons. If a swimmer competes in different events as a senior than they did as a freshman, their score can shift substantially for reasons unrelated to actual performance change. Anthony Paculba (OBU Men 2022) illustrates this clearly: his freshman season top five was anchored by distance freestyle events, the 1650, 1000, and 500 free, which tend to yield higher power points. By his senior season his portfolio had shifted entirely to sprint backstroke and mid distance events. His computed progression of -30.2 points reflects that event shift as much as it reflects any change in performance.

**Transfer freshmen missed by roster scraper.** The roster scraper identifies swimmers listed as freshmen on SwimCloud's roster page for a given season. Swimmers who transferred into a program as freshmen from another college will not appear on that page and will be missed entirely. These swimmers are not flagged as absent and they are simply never entered into the dataset.

**COVID cohort sparsity and survivorship bias.** The 2019 and 2020 entering classes had their freshman and sophomore seasons disrupted by the COVID-19 pandemic. Many swimmers from those cohorts had incomplete or missing data for their early seasons, resulting in high exclusion rates. The swimmers who do qualify from those cohorts, those who stuck around and competed despite the disruption, are a self selected group, which introduces survivorship bias into those cohort results.

**Mixed progression windows.** The overall means reported across all cohorts combine two different progression windows: four year progressions (freshman to senior season) and three year progressions (freshman to last qualifying season). These windows are not equivalent, a swimmer who left after three seasons is not directly comparable to one who completed all four years. This is disclosed throughout but not corrected for.

**Small sample sizes.** Even across four cohorts and four programs, per-team group sizes range from roughly twelve to twenty seven swimmers per gender. Means computed from samples this small are unstable and should not be used to rank programs. The results are presented as illustrative only.

## Results

Results are reported in three windows: four year (swimmers with data at their school in all four seasons), three year (swimmers with exactly three qualifying seasons), and a combined three-or-more-year window that merges both groups. All values are mean change in top five average SCY power points from freshman season to final qualifying season. These numbers are illustrative only, as sample sizes are too small to support any ranking or conclusion.

**Per-cohort results**

| Team | Gender | Cohort | 4-yr mean (n) | 3-yr mean (n) | 3+ yr mean (n) |
|---|---|---|---|---|---|
| OBU | Men | 2022 | +51.9 (6) | +16.7 (4) | +37.8 (10) |
| OBU | Men | 2021 | -33.5 (6) | +49.3 (3) | -5.9 (9) |
| OBU | Men | 2020 | +71.3 (3) | -49.0 (1) | +41.2 (4) |
| OBU | Men | 2019 | -54.6 (1) | +11.9 (3) | -4.8 (4) |
| OBU | Women | 2022 | +5.7 (2) | -27.0 (3) | -13.9 (5) |
| OBU | Women | 2021 | -18.6 (2) | -74.0 (2) | -46.3 (4) |
| OBU | Women | 2020 | +17.2 (1) | -33.6 (1) | -8.2 (2) |
| OBU | Women | 2019 | -0.9 (2) | -7.4 (5) | -5.6 (7) |
| HSU | Men | 2022 | -5.2 (4) | — | -5.2 (4) |
| HSU | Men | 2021 | +28.0 (3) | +14.4 (2) | +22.6 (5) |
| HSU | Men | 2020 | +48.2 (4) | +72.4 (1) | +53.0 (5) |
| HSU | Men | 2019 | -44.9 (5) | -90.1 (1) | -52.5 (6) |
| HSU | Women | 2022 | -23.7 (2) | -102.9 (2) | -63.3 (4) |
| HSU | Women | 2021 | +1.9 (3) | -70.8 (1) | -16.2 (4) |
| HSU | Women | 2020 | +53.5 (1) | — | +53.5 (1) |
| HSU | Women | 2019 | +16.3 (2) | -35.2 (1) | -0.9 (3) |
| DSU | Men | 2022 | +37.0 (1) | +15.8 (2) | +22.9 (3) |
| DSU | Men | 2021 | -143.8 (1) | -22.8 (1) | -83.3 (2) |
| DSU | Men | 2020 | — | +21.7 (2) | +21.7 (2) |
| DSU | Men | 2019 | +22.0 (6) | -85.9 (1) | +6.6 (7) |
| DSU | Women | 2022 | -0.7 (7) | +8.1 (2) | +1.2 (9) |
| DSU | Women | 2021 | -99.4 (1) | -49.7 (3) | -62.1 (4) |
| DSU | Women | 2020 | +65.0 (1) | -90.0 (1) | -12.5 (2) |
| DSU | Women | 2019 | -63.4 (1) | -18.8 (1) | -41.1 (2) |
| UWF | Women | 2022 | -31.6 (6) | -88.4 (1) | -39.7 (7) |
| UWF | Women | 2021 | -35.4 (1) | -20.6 (1) | -28.0 (2) |
| UWF | Women | 2020 | +20.2 (2) | +145.2 (1) | +61.9 (3) |
| UWF | Women | 2019 | +31.9 (4) | -49.8 (3) | -3.1 (7) |

**Overall means (all cohorts combined, 3+ year mixed window)**

| Team | Gender | n | Mean progression |
|---|---|---|---|
| OBU | Men | 27 | +17.5 pts |
| OBU | Women | 18 | -17.2 pts |
| HSU | Men | 20 | +2.1 pts |
| HSU | Women | 12 | -22.3 pts |
| DSU | Men | 14 | -0.6 pts |
| DSU | Women | 17 | -20.3 pts |
| UWF | Women | 19 | -8.9 pts |

## What It Would Take To Do This Properly

The pipeline built here is a proof of concept. Extending it into a study with meaningful statistical power would require several things that are beyond the current scope.

**More teams and more cohorts.** Seven group means across four cohorts is not enough data to draw conclusions about any program. A credible study would need to cover a substantial portion of Division II programs across many entering classes, where ideally a decade or more of cohorts are looked at. The current dataset covers four programs and four cohort years, which is enough to validate the methodology but not enough to rank anything.

**Proper data access.** The current dataset was built by scraping SwimCloud, which after a politely worded email exchange, asked us to stop. The dataset we have is therefore final. A larger study would require either a formal data partnership with SwimCloud, access to USA Swimming's SWIMS database, or another authoritative source of collegiate times data. Without it, the pipeline works but has nowhere left to run.

**A value added model.** Raw improvement conflates program quality with recruiting strength. A proper study would need enough data to fit a baseline, expected improvement given incoming talent level, and report each program's residual above or below that baseline. The incoming power index scores captured during scraping are a starting point for this, but fitting a reliable model requires far more observations than are currently available.

## Further Research

This project represents, to the best of my knowledge, the first attempt to systematically measure swimmer progression at the program level for any NCAA division. If you are a researcher, a data provider, or someone with access to comprehensive collegiate swimming data and interest in pursuing this question further, collaboration would be genuinely valuable. The methodology is open, the limitations are documented, and the pipeline is reproducible. The question is worth answering properly.

## Tech Stack

- **Python** — primary language for the full pipeline: scraping, database management, and analysis.
- **SQLite (via sqlite3)** — lightweight relational database used to store swimmer and times data. Chosen because the dataset is small, and does not require a server.
- **Playwright (Firefox)** — browser automation library used to scrape times data from SwimCloud's API. Required because SwimCloud is protected by Cloudflare, which blocks standard HTTP clients. A real Firefox instance with a persistent browser context is significantly harder to fingerprint as automated.
- **Requests + BeautifulSoup** — used in early development for roster scraping before Cloudflare began returning 403 responses. BeautifulSoup handles HTML parsing of roster pages.
- **osascript (Safari)** — Apple's scripting interface, used to pull HTML directly from an active Safari tab for roster pages. Even Playwright was blocked by Cloudflare Turnstile on these pages and Safari passes natively as a real browser with no automation fingerprint.
