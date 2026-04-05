# Project Review and Improvement Priorities

## Objective of This Document

Note:

This review was initially written against the earlier version of the project, before the scraping utilities were strengthened and before Question 3 was replaced. It remains useful as a grading-oriented review of the original submission risks, especially around data reliability. After the refactor, the main methodological weakness identified here for Question 3 has been addressed by replacing the loyalty-based analysis with an artist-diversity analysis based on artist tags.

This document combines two complementary reviews of the project:

- a first pass focused on functional coverage of the assignment;
- a second pass from a professor / grader perspective, focused on likely weaknesses, risks, and what should be improved to obtain the best possible grade.

The goal is not to criticize the project unnecessarily. The goal is to identify what is already good, what is only partially convincing, and what should be improved first.

---

## 1. Overall Assessment

### Short answer

The project **mostly satisfies the assignment requirements**, but it does **not yet present the strongest possible final deliverable**.

It has clear strengths:

- more than 3 resources were scraped from the same site;
- data is stored in separate CSV files;
- 3 analysis questions are defined;
- multiple plots are generated;
- several real data transformations are used.

However, it also has important weaknesses:

- part of the scraped data is incomplete or unreliable;
- one resource (`users.csv`) is formally collected but is almost unusable analytically;
- Question 3 does not really use user data even though user profiles were scraped;
- some metrics are only proxies and should be presented more carefully;
- the README is incomplete as a final deliverable.

---

## 2. First Pass: Functional Review Against the Assignment

## 2.1 Part 1: Data Collection

### Requirement: Develop a Python script to interact automatically with the site

Status: **Yes**

Relevant files:

- `scraping/run_all.py`
- `scraping/scraper_genres.py`
- `scraping/scraper_artists.py`
- `scraping/scraper_albums.py`
- `scraping/scraper_tracks.py`
- `scraping/scraper_users.py`

### Requirement: Correctly manage waiting time for web content loading

Status: **Yes, partially convincing**

Relevant files:

- `scraping/utils.py`
- `scraping/config.py`

The project uses `polite_sleep()` and a `REQUEST_DELAY`. This is good for respectful scraping and basic timing control.

Limitation:

- this is not true dynamic content handling;
- it is just fixed delay management;
- `selenium` is listed in the dependencies but is not actually used.

For the assignment, this is probably acceptable, but it is not especially advanced.

### Requirement: Extract at least 3 different resources from the same website

Status: **Yes**

Resources extracted:

- genres
- artists
- albums
- tracks
- users

This exceeds the minimum requirement.

### Requirement: Use web scraping techniques

Status: **Yes**

The project uses:

- `requests`
- `BeautifulSoup`
- HTML selectors

### Requirement: Save extracted data in tabular format

Status: **Yes**

All datasets are saved as CSV files.

### Requirement: Create a separate `.csv` file for each resource

Status: **Yes**

Generated files:

- `data/genres.csv`
- `data/artists.csv`
- `data/albums.csv`
- `data/tracks.csv`
- `data/users.csv`

### Part 1 conclusion

Part 1 is **fulfilled**.

Important nuance:

The formal requirements are met, but the **quality of the resources is uneven**. The project is much stronger on artists / tracks than on users.

## 2.2 Part 2: Data Manipulation and Visualization

### Requirement: Define 2 to 3 relevant questions

Status: **Yes**

Questions currently used:

1. Which musical genres are the most hybrid?
2. Is there a link between a music's duration and its popularity?
3. Do the biggest artists have loyal fans?

### Requirement: Perform at least one transformation seen in class

Status: **Yes**

Transformations clearly present in the code:

- parsing semicolon-separated tags;
- deduplication of tag lists;
- filtering invalid rows;
- creation of duration categories;
- computation of ratios;
- `groupby` aggregations;
- co-occurrence counting;
- log transformation for popularity variables.

### Requirement: Answer the questions with plots or extracted information

Status: **Yes**

The analysis scripts produce:

- plots in `analysis/plots/`;
- summary findings in the console.

### Part 2 conclusion

Part 2 is **fulfilled**.

Important nuance:

The analyses exist and are readable, but not all of them are equally convincing from a methodological perspective.

---

## 3. Second Pass: Professor / Grader Review

This section focuses on what a grader is likely to notice quickly.

## 3.1 Main strengths a grader would likely appreciate

### 1. The project is complete and structured

The repository has a clean separation between:

- scraping;
- raw data;
- analysis;
- outputs;
- documentation.

That is a strong organizational point.

### 2. The scope is ambitious enough

The team did not stop at the minimum of 3 resources. Scraping 5 resources from the same platform shows initiative.

### 3. The project has a coherent story

The site choice, the resources, and the questions are all connected around Last.fm and music listening behavior.

### 4. The visual output is substantial

There are many plots, and the analysis scripts are not trivial. This gives the impression of a real end-to-end project.

## 3.2 Main weaknesses a grader would likely criticize

### 1. `users.csv` is weak and almost unused

This is probably the biggest issue.

Observed problems:

- `country` is almost always missing;
- `top_genres` is completely missing;
- `age` remains 0;
- `playlists_count` remains 0;
- Question 3 does not really use this dataset.

What a grader may conclude:

- the project scraped the resource, but did not manage to extract meaningful profile information;
- the resource exists more to satisfy quantity than to support the final analysis.

This does not invalidate the project, but it weakens the perceived rigor.

### 2. Some analyses rely on proxy metrics that should be justified better

The key example is Question 3.

Current definition:

- loyalty = `play_count / listeners`

This is reasonable as a proxy, but it is **not direct user loyalty**.

What a grader may ask:

- Why is this a valid measure of loyalty?
- Does this ratio reflect fan devotion, replay behavior, artist age, or platform exposure?
- Why collect users if loyalty is computed only from artist-level stats?

If the oral defense is weak here, the analysis may look conceptually fragile.

### 3. Some scraped fields are incomplete

Observed examples:

- many tracks have `duration_seconds = 0`;
- many albums have `listeners = 0`, `play_count = 0`, or `num_tracks = 0`;
- some artists have missing tags.

What a grader may conclude:

- scraping worked, but coverage is incomplete;
- conclusions may depend on a filtered subset rather than the whole sample.

This should be acknowledged explicitly in the report.

### 4. The sampling strategy may introduce bias

Current process starts from a fixed list of seed genres and then collects artists from those tag pages.

This creates several biases:

- genre bias;
- popularity bias;
- Last.fm page-availability bias;
- limited artist and track caps.

A careful grader may not object to the existence of bias, but will expect the team to mention it.

### 5. The project sometimes looks more descriptive than analytical

Question 1 is fairly analytical.

Question 2 is decent but still mostly descriptive, unless the team explains the correlation results carefully.

Question 3 risks sounding more assertive than the data truly allows.

For a better grade, the presentation should clearly distinguish:

- observed pattern;
- inferred interpretation;
- unsupported speculation.

### 6. The README is not fully finished as a deliverable

Current issue:

- the video link placeholder is still empty.

A grader may interpret this as an unfinished submission detail.

## 3.3 Risk ranking from highest to lowest

### High priority risks

- `users.csv` is low quality and barely used.
- Question 3 is weaker methodologically than Questions 1 and 2.
- Missing / zero values reduce the strength of some conclusions.

### Medium priority risks

- Bias in the scraping sample is not explicitly discussed enough.
- Some metrics look improvised unless justified carefully.

### Lower priority risks

- `selenium` is included but not used.
- README final polish is incomplete.

---

## 4. File-by-File Evaluation Summary

## 4.1 Root files

### `README.txt`

What it does:

- explains the project;
- presents the group;
- shows commands to run scraping and analysis.

Evaluation:

- useful and readable;
- should better highlight limitations;
- should not leave the video link empty in a final submission.

### `requirements.txt`

What it does:

- lists dependencies.

Evaluation:

- correct;
- some listed packages are not actually used in the visible code.

## 4.2 Scraping files

### `scraping/config.py`

What it does:

- centralizes constants;
- controls delay, seed genres, output folder, scraping limits.

Evaluation:

- clean and useful;
- makes the project configurable;
- also reveals the hard limits that constrain dataset size.

### `scraping/utils.py`

What it does:

- page fetching;
- number parsing;
- sleep handling.

Evaluation:

- well factored;
- helps code reuse;
- basic but effective.

### `scraping/scraper_genres.py`

What it does:

- scrapes tag pages for genres;
- stores genre-level summary information.

Evaluation:

- valid for building a seed dataset;
- `reach` is quite rough and should be described as an approximate indicator, not a precise metric.

### `scraping/scraper_artists.py`

What it does:

- collects artists from tag pages;
- enriches artist stats and tags from artist pages.

Evaluation:

- one of the strongest scrapers in the repo;
- directly supports Questions 1 and 3.

### `scraping/scraper_albums.py`

What it does:

- collects album pages from each artist;
- enriches albums with listeners, play count, tags, track count.

Evaluation:

- useful as an additional resource;
- data completeness is only moderate.

### `scraping/scraper_tracks.py`

What it does:

- collects top tracks for each artist;
- enriches tracks with duration and stats.

Evaluation:

- essential for Question 2;
- overall useful;
- weakened by missing durations for many tracks.

### `scraping/scraper_users.py`

What it does:

- collects usernames from artist listener pages;
- attempts to extract user-level metadata.

Evaluation:

- formally valid;
- analytically weak;
- the least convincing scraper in the project.

### `scraping/run_all.py`

What it does:

- orchestrates the full scraping pipeline.

Evaluation:

- good project entry point;
- useful for reproducibility.

## 4.3 Analysis files

### `analysis/question1_genre_hybridity.py`

What it does:

- uses artist tags to study genre co-occurrence;
- computes frequency, unique partners, pair counts, hybrid ratios;
- generates 4 plots.

Evaluation:

- probably the best analysis in the repo;
- directly connected to the scraped artist tags;
- method is understandable and defendable.

### `analysis/question2_duration_popularity.py`

What it does:

- filters tracks with valid durations;
- creates duration categories;
- compares duration to popularity;
- computes correlation;
- generates 4 plots.

Evaluation:

- good question;
- real transformations are present;
- conclusions must be presented carefully because they rely only on tracks with duration available.

### `analysis/question3_loyal_fans.py`

What it does:

- computes a loyalty ratio from artist-level metrics;
- compares loyalty by artist popularity and primary genre;
- generates 4 plots.

Evaluation:

- interesting idea;
- weakest question conceptually;
- strongest risk of critique during grading.

---

## 5. Output Quality Review

## 5.1 Datasets

### `genres.csv`

Strength:

- clean and complete.

Weakness:

- descriptive only;
- metrics are rough.

### `artists.csv`

Strength:

- strong dataset;
- central to the project.

Weakness:

- some missing tags.

### `albums.csv`

Strength:

- useful additional resource.

Weakness:

- many zero values for important fields.

### `tracks.csv`

Strength:

- rich enough for Question 2.

Weakness:

- duration is missing for a significant subset of tracks.

### `users.csv`

Strength:

- satisfies the formal requirement of another resource.

Weakness:

- most fields are not informative;
- weak support for real analysis.

## 5.2 Plots

Strengths:

- enough plots to show real analytical work;
- plot naming is clear;
- each question has a dedicated plot set.

Weaknesses:

- the project should explicitly state which plots are the strongest evidence and which are secondary.

---

## 6. What Should Be Improved First to Maximize the Grade

This is the most important section.

## Priority 1: Strengthen the analytical honesty of the presentation

The team should explicitly say:

- some scraped fields are incomplete;
- not every resource is equally reliable;
- Question 3 uses a proxy metric, not direct user loyalty;
- conclusions apply to the scraped sample, not to all music on Last.fm.

This alone would immediately make the project sound more rigorous.

## Priority 2: Reframe Question 3 carefully

The current question is acceptable, but it should be defended more cautiously.

Recommended presentation angle:

- not "we measure true fan loyalty";
- but "we approximate loyalty through average scrobbles per listener".

The distinction matters a lot in evaluation.

## Priority 3: Put more emphasis on the strongest parts

In the report and oral presentation:

- emphasize Question 1 first;
- use Question 2 as a moderate-strength result;
- present Question 3 as exploratory.

This ordering improves credibility.

## Priority 4: Explicitly discuss missing data

The report should mention:

- how many tracks have valid durations;
- how many albums have valid stats;
- that user profile data is sparse.

A grader is much more forgiving when limitations are acknowledged clearly.

## Priority 5: Improve the README and final packaging

The final submission should not contain obvious unfinished elements.

At minimum:

- replace the video placeholder;
- add a brief limitations section;
- mention the main transformations used in the analysis.

---

## 7. Concrete Things That Should Be Modified

This section focuses on what should be changed in the project deliverable, not necessarily in the code first.

## 7.1 In the README / report

- Add a short "limitations" section.
- Explain that `users.csv` is incomplete and not the main analytical source.
- Explain the exact meaning of the loyalty ratio.
- State that `reach` in `genres.csv` is an approximate indicator.
- Mention the effective sample sizes used in Q2 and Q3.
- Complete the video presentation section.

## 7.2 In the oral defense

- Do not oversell the user scraping quality.
- Do not claim causation from correlation in Question 2.
- Do not claim direct measurement of fan loyalty in Question 3.
- Use careful wording such as:
  - "in our scraped sample"
  - "suggests"
  - "is associated with"
  - "proxy indicator"

## 7.3 In the project narrative

- Present the project as a study of Last.fm metadata and listening behavior.
- Show that data collection decisions affect analytical conclusions.
- Explain why some questions are stronger than others.

---

## 8. Better Question Ideas Based on Last.fm

The following alternatives are generally more natural for Last.fm and may lead to stronger analyses than the current Question 3.

## 8.1 Strong alternatives using artist and track data

### 1. Do artists with more genre tags attract more listeners?

Why it is interesting:

- directly connected to Last.fm tagging culture;
- easy to justify;
- can use `artists.csv`.

Possible analysis:

- number of tags vs listeners;
- number of tags vs play count;
- comparison by genre family.

### 2. Are tracks with more niche tags less popular than mainstream-tagged tracks?

Why it is interesting:

- links popularity to musical categorization;
- fits Last.fm well.

Possible analysis:

- identify common vs rare tags;
- compare listeners/play count across tag rarity levels.

### 3. Do some genres have longer songs on average than others?

Why it is interesting:

- clear, interpretable;
- very natural with track duration data.

Possible analysis:

- average duration by genre;
- duration distribution by primary tag;
- identify genres with most extreme durations.

### 4. Are an artist's most popular tracks also their longest or shortest ones?

Why it is interesting:

- artist-level comparison is more controlled;
- avoids some cross-artist popularity bias.

Possible analysis:

- within each artist, rank tracks by popularity and compare durations;
- visualize per-artist differences.

### 5. Do highly popular artists have more stylistic diversity than smaller artists?

Why it is interesting:

- very compatible with Last.fm tags;
- stronger concept than "loyal fans" if user data is weak.

Possible analysis:

- number of unique tags per artist;
- tag entropy or diversity proxy;
- compare diversity vs listeners.

## 8.2 Strong alternatives if user data becomes usable

### 6. Do listeners of niche artists have higher scrobble counts than listeners of mainstream artists?

Why it is interesting:

- actually uses user data meaningfully;
- closer to a real loyalty / engagement question.

### 7. Are older Last.fm users more associated with specific genres than newer users?

Why it is interesting:

- uses `registered_year`;
- leverages the platform-specific social dimension of Last.fm.

### 8. Are fans of certain genres more active on Last.fm?

Why it is interesting:

- directly platform-native;
- works well if top genres and profile activity are extracted reliably.

## 8.3 Best replacement candidates for the current Question 3

If only one question should be replaced, the best candidates are probably:

1. Do highly popular artists have more stylistic diversity than smaller artists?
2. Do artists with more genre tags attract more listeners?
3. Do some genres have longer songs on average than others?

These questions are easier to defend with the current data quality.

---

## 9. Final Recommendation

If the team cannot change much technically before submission, the best strategy is:

- keep the current project structure;
- present Questions 1 and 2 as the strongest results;
- present Question 3 as exploratory and proxy-based;
- openly acknowledge the limitations of the user data;
- polish the README and final presentation materials.

If the team still has time for deeper improvement, the biggest gain would come from:

- making user scraping genuinely usable;
- or replacing Question 3 with a stronger question based on artist / track / tag data.

In short:

- the project is valid;
- it is not weak overall;
- but the final grade will depend heavily on how honestly and intelligently the limitations are presented.
