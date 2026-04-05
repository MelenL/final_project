PROGRAMMING FOR DATA SCIENCE
FINAL PROJECT – GROUP 5

============================================================
GROUP INFORMATION
============================================================

Group: 5

Student 1
Name: Melen Laclais
Student number: 999924
UPM ID: LH78L8K56
Email: melen.laclais@alumnos.upm.es

Student 2
Name: Khulan Bayarkhuu
Student number: 250836
UPM ID: L73MGJTLW
Email: khulan.bayarkhuu@alumnos.upm.es

Student 3
Name: Camille Ansel
Student number: 999930
UPM ID: 23EK55858
Email: ansel.camille@alumnos.upm.es

Student 4
Name: Léo LAMY
UPM ID: H2V2L49R4
Email: leo.lamy@alumnos.upm.es

============================================================
Last.fm Web Scraping and Music Data Analysis
============================================================

This project collects music-related data from the Last.fm website through
automatic web scraping and stores the results in CSV files.

The scraping phase gathers several resources from the same website, including
musical genres, artists, albums, tracks, and user profiles. The project then
uses these datasets to perform data analysis and visualization.

The scraping pipeline was designed to be more robust than a single-selector
approach. It uses multiple HTML fallbacks for important fields such as tags,
listeners, play counts, and track duration. It also computes data quality
indicators for several resources in order to make incomplete extractions easier
to identify during analysis.

The final goal of the analysis is to answer three music-related questions:
1. Which musical genres are the most hybrid ?
2. Is there a link between a music’s duration and its popularity?
3. Are songs from some genres systematically longer than songs from others on Last.fm?

Website used for scraping:
https://www.last.fm

============================================================
PROJECT STRUCTURE AND MODULE DESCRIPTIONS
============================================================

final_project/
│
├── scraping/               Web scraping pipeline (Part 1)
│   ├── config.py           Global settings: base URL, HTTP headers, seed genres,
│   │                       request delay, and output directory path.
│   ├── utils.py            Shared helper functions used by all scrapers:
│   │                         - fetch_page()               : HTTP GET with retries
│   │                         - extract_tag_list()         : genre tag extraction
│   │                         - extract_listener_playcount(): listeners/scrobbles
│   │                         - extract_duration_seconds() : track duration parsing
│   │                         - parse_abbr_number()        : "8.2M" → 8200000
│   │                         - completeness_ratio()       : data_quality score
│   │                         - polite_sleep()             : rate-limit delay
│   ├── scraper_genres.py   Scrapes /tag/GENRE/artists for each seed genre.
│   │                       Produces: genres.csv
│   ├── scraper_artists.py  Two-pass scraper: collects artist names from genre
│   │                       pages, then enriches each with listeners, play count,
│   │                       and genre tags from individual artist pages.
│   │                       Produces: artists.csv
│   ├── scraper_albums.py   Two-pass scraper: collects album names per artist,
│   │                       then enriches each with listeners, play count, and
│   │                       track count from individual album pages.
│   │                       Produces: albums.csv
│   ├── scraper_tracks.py   Two-pass scraper: collects track names from artist
│   │                       listing pages, then visits each track page for
│   │                       duration, play count, and tags.
│   │                       Produces: tracks.csv
│   ├── scraper_users.py    Discovers usernames from artist listener pages, then
│   │                       scrapes each user profile for scrobble count, country,
│   │                       registration year, and genre preferences.
│   │                       Produces: users.csv
│   └── run_all.py          Master script that runs all five scrapers in order.
│                           Clears previous CSV files before each run.
│                           Entry point for the full scraping pipeline.
│
├── analysis/               Data analysis and visualisation (Part 2)
│   ├── question1_genre_hybridity.py
│   │                       Analyses which genres are the most hybrid by measuring
│   │                       genre co-occurrence across artist tag profiles.
│   │                       Input: data/artists.csv
│   │                       Output: 4 plots (q1_*.png)
│   ├── question2_duration_popularity.py
│   │                       Analyses the relationship between track duration and
│   │                       popularity (listeners and play count), using log
│   │                       transforms, duration bins, and Pearson correlation.
│   │                       Input: data/tracks.csv
│   │                       Output: 4 plots (q2_*.png)
│   ├── question3_genre_duration.py
│   │                       Analyses whether track duration differs systematically
│   │                       across genres, using average, median, and standard
│   │                       deviation of duration per primary genre.
│   │                       Input: data/tracks.csv
│   │                       Output: 4 plots (q3_*.png)
│   └── plots/              Directory where all generated PNG plots are saved.
│
├── data/                   CSV datasets produced by the scraping phase.
│   ├── genres.csv          50 music genres with top artists and reach proxy.
│   ├── artists.csv         200 artists with listeners, play count, and tags.
│   ├── albums.csv          594 albums with listeners, play count, and track count.
│   ├── tracks.csv          1000 tracks with duration, listeners, and genre tags.
│   └── users.csv           449 user profiles with scrobble count and metadata.
│
├── requirements.txt        List of Python package dependencies with pinned versions.
└── README.txt              This file.


============================================================
DEPENDENCIES
============================================================

The project requires Python 3 and the following packages:

Package            Version   Purpose
-----------------  -------   -----------------------------------------------
requests           2.31.0    HTTP requests to fetch Last.fm pages
beautifulsoup4     4.12.3    HTML parsing and CSS selector extraction
lxml               5.1.0     Fast HTML parser backend for BeautifulSoup
selenium           4.18.1    Imported as a dependency; browser automation
                             (not actively used — scraping is done via requests)
webdriver-manager  4.0.1     Manages browser drivers for Selenium
pandas             2.2.1     Data loading, cleaning, and transformation
numpy              1.26.4    Numerical operations (log transforms, polynomial fit)
matplotlib         3.8.3     Base plotting library
seaborn            0.13.2    Statistical visualisation (heatmaps, boxplots)
scipy              1.12.0    Statistical functions (available for future tests)


============================================================
INSTALLATION
============================================================

Install all dependencies with:

  pip install -r requirements.txt

Or manually:

  pip install requests==2.31.0 beautifulsoup4==4.12.3 lxml==5.1.0 \
              selenium==4.18.1 webdriver-manager==4.0.1 pandas==2.2.1 \
              matplotlib==3.8.3 seaborn==0.13.2 numpy==1.26.4 scipy==1.12.0


============================================================
RUNNING THE SCRAPING PHASE
============================================================

Execute from the project root:

  cd scraping
  python run_all.py

run_all.py orchestrates all five scrapers in sequence (genres → artists →
albums → tracks → users) and writes the results to data/.

Important:
- Previous CSV files in data/ are deleted at the start of each run.
- The full pipeline takes several minutes due to polite delays between requests.
- Individual scrapers can also be run standalone for testing:
    python scraper_artists.py
    python scraper_tracks.py
    (etc.)


============================================================
RUNNING THE ANALYSIS PHASE
============================================================

The CSV files in data/ must exist before running the analysis.
Execute from the project root:

  cd analysis
  python question1_genre_hybridity.py   # Genre hybridity analysis
  python question2_duration_popularity.py  # Duration vs. popularity
  python question3_genre_duration.py    # Duration by genre

Each script:
- reads from data/ (relative path, so must be run from the analysis/ folder
  or from the project root as shown above);
- prints key findings to the console;
- saves plots as PNG files in analysis/plots/.


============================================================
OUTPUTS GENERATED
============================================================

Scraping output:
The scraping phase generates CSV files in the data/ folder:
- genres.csv
- artists.csv
- albums.csv
- tracks.csv
- users.csv

Additional notes on the CSV structure:
- `artists.csv` includes artist-level tags and quality indicators such as
  `tag_count` and `data_quality`;
- `albums.csv`, `tracks.csv`, and `users.csv` include a `data_quality` column;
- each new scraping run replaces the previous CSV files.

Analysis output:
The analysis scripts generate plots in:
analysis/plots/

Examples of generated PNG files include:
- q1_genre_cooccurrence_heatmap.png
- q1_hybrid_genres_total_cooccurrences.png
- q1_hybrid_genres_unique_partners.png
- q1_top_genre_pairs.png
- q2_duration_distribution.png
- q2_duration_vs_popularity_scatter.png
- q2_popularity_by_duration_boxplot.png
- q2_avg_popularity_by_duration.png
- q3_avg_duration_by_genre.png
- q3_duration_distribution_by_genre.png
- q3_longest_genres.png
- q3_duration_variability_by_genre.png


============================================================
METHODOLOGICAL NOTE
============================================================

Not every scraped resource has the same reliability.

In practice:
- artist and track data are the strongest resources for analysis;
- album and user data may contain more missing fields depending on the pages
  available on Last.fm;
- the `data_quality` columns help identify which rows are more complete;
- for the most meaningful analytical results, it is recommended to rerun the
  scraping phase before running the analysis phase so that all datasets match
  the current version of the code.

How data_quality is computed:
  The value is the share of populated fields among the fields that matter
  for a given resource. It is computed by the completeness_ratio() function
  in scraping/utils.py using the following formula:

    data_quality = number of populated fields / total number of checked fields

  A field is considered populated if:
  - for strings : the value is non-empty after stripping whitespace;
  - for numbers : the value is non-zero (a 0 indicates extraction failure).

  The fields checked differ per resource:
  - artists : listeners, play_count, top_tags            (3 fields)
  - tracks  : duration_seconds, listeners, play_count,
              tags                                        (4 fields)
  - albums  : listeners, play_count, tags, num_tracks    (4 fields)
  - users   : country, scrobble_count, top_genres,
              playlists_count, registered_year           (5 fields)

  Examples:
  - An artist with listeners=8M, play_count=1.3B, top_tags="rock;pop"
    scores 3/3 = 1.0
  - A track with duration=235, listeners=4M, play_count=0, tags="rock"
    scores 3/4 = 0.75  (play_count was not extracted)
  - A user with only scrobble_count and registered_year populated
    scores 2/5 = 0.4  (country, top_genres, playlists_count are missing)


============================================================
DATASET DESCRIPTION AND QUALITY
============================================================

Five CSV files are produced by the scraping phase. Below is a description of
each dataset, its columns, and an honest assessment of its quality.

------------------------------------------------------------
genres.csv  (50 rows)
------------------------------------------------------------
Columns:
  name              : genre name (e.g., "rock", "hip-hop")
  url               : canonical Last.fm tag URL
  reach             : rough proxy computed as the number of .link-block-target
                      elements on the tag page (not an official Last.fm metric)
  top_artists       : semicolon-separated list of up to 10 artists tagged
                      with this genre
  num_artists_tagged: number of artists listed on that genre page

Quality:
  All 50 rows are fully populated. The `reach` column is a count of
  clickable page elements, which serves as a relative engagement proxy
  rather than an exact listener figure. The 50 genres were chosen from
  a curated seed list covering mainstream and niche styles, ensuring
  good variety. This dataset is complete and reliable.

------------------------------------------------------------
artists.csv  (200 rows)
------------------------------------------------------------
Columns:
  name         : artist name
  listeners    : total unique listeners on Last.fm
  play_count   : total scrobbles (plays)
  url          : artist page URL
  top_tags     : up to 5 semicolon-separated genre tags
  tag_count    : number of tags successfully extracted
  data_quality : share of populated fields (0.0 to 1.0)

Quality:
  Mean data_quality = 0.99. Nearly all artists have valid listeners,
  play counts, and tags. Average tag count = 5.2 per artist, confirming
  rich multi-genre profiles. This is the strongest dataset and is the
  primary source for Question 1.

  Caveat: artists were collected from genre tag pages, so the sample
  is biased towards popular, well-documented acts. Niche or very new
  artists are underrepresented.

------------------------------------------------------------
tracks.csv  (1000 rows)
------------------------------------------------------------
Columns:
  name             : track title
  artist           : associated artist name
  duration_seconds : track length in seconds (0 if extraction failed)
  listeners        : number of unique listeners for this track
  play_count       : total play count for this track
  url              : individual track page URL
  tags             : semicolon-separated genre tags (inherited from artist
                     and enriched from track page when available)
  data_quality     : share of populated fields (0.0 to 1.0)

Quality:
  945 out of 1000 tracks (94.5%) have a valid duration (> 0 seconds).
  Mean data_quality = 0.98. Duration ranges from ~1 to ~16 minutes with
  a mean of ~4 minutes, which is consistent with real-world music norms.
  The 55 tracks with duration = 0 were excluded from analysis.

  Caveat: tracks were scraped as the top 5 tracks per artist, so only
  commercially prominent songs are included. Obscure deep cuts are absent,
  which may slightly bias duration and popularity distributions upward.

------------------------------------------------------------
albums.csv  (594 rows)
------------------------------------------------------------
Columns:
  name         : album title
  artist       : associated artist name
  listeners    : album listeners
  play_count   : album play count
  url          : album page URL
  tags         : semicolon-separated genre tags
  num_tracks   : number of tracks found in the tracklist
  data_quality : share of populated fields (0.0 to 1.0)

Quality:
  Mean data_quality = 0.97. Listener and play-count figures are well
  populated. Albums were not used in the three analysis questions because
  the track-level data offers finer granularity; album-level aggregation
  would lose the duration dimension needed for Questions 2 and 3.

------------------------------------------------------------
users.csv  (449 rows)
------------------------------------------------------------
Columns:
  username       : Last.fm username
  country        : user's listed country (often empty)
  age            : user's listed age (rarely available)
  scrobble_count : total scrobbles on the account
  url            : user profile URL
  top_genres     : genres found on the profile page
  playlists_count: number of playlists
  registered_year: year the account was created
  data_quality   : share of populated fields (0.0 to 1.0)

Quality:
  Mean data_quality = 0.39 — by far the weakest dataset. Only 1 user has
  a listed country; age and top_genres are almost always missing. This is
  a structural limitation of Last.fm: user profiles are sparse by default
  and the site does not expose personal data prominently.

  Scrobble counts are well scraped (high values confirming active users),
  but the demographic and preference fields are essentially unusable for
  analysis. This is why users.csv was not used in the analysis questions.

------------------------------------------------------------
WHY THESE QUESTIONS WERE CHOSEN (DATA QUALITY RATIONALE)
------------------------------------------------------------

The three analysis questions were chosen specifically to exploit the two
highest-quality datasets (artists.csv and tracks.csv):

  Question 1 — Genre Hybridity:
    Uses the `top_tags` column of artists.csv, which is nearly complete
    (200 artists, mean 5.2 tags each). The multi-tag structure of Last.fm
    artist profiles is exactly what is needed to measure genre co-occurrence.
    No other dataset provides this kind of genre overlap signal.

  Question 2 — Duration vs. Popularity:
    Uses `duration_seconds`, `listeners`, and `play_count` from tracks.csv.
    945 valid durations and a near-complete popularity signal (data_quality
    0.98) make this dataset ideal for a correlation and distribution study.

  Question 3 — Genre Duration by Genre:
    Also uses tracks.csv, combining `duration_seconds` with the `tags`
    column to assign a primary genre to each track. The tag inheritance
    strategy (artist tags passed to tracks, enriched per-track when
    available) ensures broad genre coverage across the 1000 tracks.

  The overall approach was to scrape as much data as possible from the
  site first, then decide which questions to ask based on what the data
  could actually support — rather than fixing questions upfront and
  risking being unable to answer them. Albums and users were deliberately
  excluded from the analysis because albums lack the duration dimension
  and users lack reliable demographic or preference data
  (data_quality = 0.39). Analysing incomplete data without acknowledging
  its limits would produce misleading results.


============================================================
ANALYSIS RESULTS
============================================================

This section summarises the main findings for each question, grounded
in the plots generated by the analysis scripts.

------------------------------------------------------------
QUESTION 1 — Which musical genres are the most hybrid?
------------------------------------------------------------

Method:
  Genre hybridity is measured in two complementary ways:
  (a) unique partner count: how many distinct genres a given genre
      co-occurs with across all artist tag profiles;
  (b) total co-occurrence count: how often a genre appears alongside
      another genre (sums all pairings).
  The co-occurrence heatmap adds a visual overview of the strongest links
  among the 12 most frequent genres.

Key findings from the plots:

  1. pop is the most hybrid genre by unique partner diversity, appearing
     alongside more than 75 distinct genres across 43 artists. This means
     pop acts on Last.fm draw tags from an exceptionally wide stylistic
     vocabulary.

  2. alternative, indie, and rock form the core hybrid hub. Each appears
     in ~55-70 unique genre pairings and has the highest total
     co-occurrence counts (all at the maximum hybridity ratio of 4.00,
     meaning every artist tagged with these genres also carries at least
     4 other genre tags). This is consistent with their role as broad
     umbrella genres in popular music.

  3. female vocalists stands out as a cross-genre descriptor rather than
     a musical style — it co-occurs with pop, r&b, soul, indie, and many
     others, explaining its high unique partner count.

  4. The heatmap reveals the strongest pairings by raw count:
       - rock + alternative  (32 co-occurrences)
       - indie + alternative (28 co-occurrences)
       - pop  + rock         (15 co-occurrences)
     These pairs reflect well-known genre adjacencies in Western popular
     music and validate the scraping: the data reproduces culturally
     expected relationships.

  5. Genre clusters visible in the heatmap:
       - A mainstream cluster: pop, rock, alternative, indie
       - A hip-hop / R&B cluster: hip-hop, r&b, rap
       - Instrumental genres (jazz, classical, electronic) are more
         isolated, indicating fewer overlapping tags with pop styles.

  Conclusion:
    pop, alternative, indie, and rock are the most hybrid genres in this
    Last.fm sample. They act as mixing hubs, consistently co-appearing
    with a wide variety of other styles. Specialised genres (jazz,
    classical, metal) are comparatively insular, connected mainly to
    their own sub-genre family.

------------------------------------------------------------
QUESTION 2 — Is there a link between music duration and popularity?
------------------------------------------------------------

Method:
  Track duration (in seconds) is compared against two popularity proxies:
  listener count and play count. Durations are also grouped into
  six categorical bins (< 2 min, 2-3, 3-4, 4-5, 5-7, > 7 min).
  Log10 transformation is applied to popularity values to handle the
  heavy right-skew of listener/play-count distributions.
  Pearson correlation is computed to quantify the linear relationship.

Key findings from the plots:

  1. Duration distribution (q2_duration_distribution.png):
     The bulk of tracks cluster in the 3-4 minute range (382 tracks,
     the tallest bar), with mean = 4.0 min and median = 3.8 min. This
     closely matches the standard radio-friendly format. Very few tracks
     are under 2 minutes (31) or over 7 minutes (37).

  2. Scatter + polynomial trend (q2_duration_vs_popularity_scatter.png):
     The polynomial trend line shows a clear inverted-U shape: popularity
     (both listeners and play count) rises from 1 minute, peaks around
     3-5 minutes, then falls off significantly for longer tracks. Songs
     beyond 8-10 minutes sit consistently in the lower-popularity zone.

  3. Average popularity by duration category
     (q2_avg_popularity_by_duration.png):
     The 4-5 min bin has the highest average listener count (~1.1M).
     The 3-4 min bin follows closely. Songs under 2 min and over 7 min
     have notably lower averages. Sample sizes are unequal (n=31 for
     < 2 min vs n=392 for 3-4 min), which must be interpreted with
     caution.

  4. Box plot (q2_popularity_by_duration_boxplot.png):
     The median log-listeners is fairly stable across 2-3, 3-4, 4-5 and
     5-7 minute categories (~6.0 on log10 scale, i.e. ~1M listeners),
     but the > 7 min category shows a clear downward shift. The
     < 2 min category also has higher variance, reflecting a mix of
     viral short clips and forgotten intros.

  5. Pearson correlation is near 0 (typically -0.05 to +0.05). This is
     expected: the relationship is non-linear (inverted-U), not linear,
     so the Pearson coefficient underestimates the real pattern.

  Conclusion:
    There is no strong linear correlation between duration and popularity,
    but the data reveals a structural sweet spot: tracks in the 3-5 minute
    range tend to accumulate more listeners than very short or very long
    songs. This reflects the dominance of the standard pop/rock song
    format on Last.fm. The relationship is better described as a
    diminishing-returns curve than a linear trend.

------------------------------------------------------------
QUESTION 3 — Are songs from some genres systematically longer?
------------------------------------------------------------

Method:
  Each track is assigned a primary genre based on the first tag in its
  tag list. Only genres with at least 12 tracks are retained to ensure
  statistical robustness. Average and median duration are computed per
  genre. Standard deviation is used to measure within-genre variability.

Key findings from the plots:

  1. Genres with the longest average tracks
     (q3_avg_duration_by_genre.png, q3_longest_genres.png):
       - classical:   ~4.7 min average (median = 4.06 min, n=80)
       - heavy metal: ~4.6 min average (median = 4.72 min, n=16)
       - metal:       ~4.5 min average (median = 4.49 min, n=26)
       - electronic:  ~4.4 min average (median = 3.88 min, n=27)
       - jazz:        ~4.3 min average (median = 3.60 min, n=58)

  2. Genres with the shortest average tracks:
       - dance:       ~3.1 min average
       - indie rock:  ~3.2 min average
       - pop:         ~3.4 min average

  3. Duration gap:
     The difference between the longest (classical, ~4.7 min) and
     shortest (dance, ~3.1 min) genre averages is approximately 1.6
     minutes — a meaningful difference representing roughly 40% of
     the shortest average duration.

  4. Duration variability (q3_duration_variability_by_genre.png):
     Classical has the widest standard deviation (~3.3 min), followed
     by jazz (~2.5 min). This reflects the extreme format range of
     these genres: a Chopin nocturne lasts 4 minutes while a symphony
     movement may run 15+. The boxplot confirms classical and jazz
     produce the most outliers at the high end (up to 13+ minutes).

     In contrast, pop, dance, and indie rock show tighter distributions,
     confirming a more standardised commercial song format.

  5. Box plot across major genres
     (q3_duration_distribution_by_genre.png):
     Classical has the widest interquartile range and the highest
     upper whisker. Pop has one of the narrowest boxes (low variability).
     Hip-hop shows moderate variability, consistent with mixing short
     singles and long album cuts.

  Conclusion:
    Yes — genre is systematically associated with track duration in this
    Last.fm sample. Classical, heavy metal, and jazz produce the longest
    tracks on average, while dance and pop tracks are shorter and more
    uniform. These differences reflect real compositional conventions:
    classical and jazz allow extended structures, whereas dance and pop
    are optimised for radio and streaming consumption.


============================================================
VIDEO PRESENTATION
============================================================

Video link:
[INSERT LINK HERE]
