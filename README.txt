PROGRAMMING FOR DATA SCIENCE
FINAL PROJECT – GROUP 5

============================================================
1. GROUP INFORMATION
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

The final goal of the analysis is to answer three music-related questions:
1. What are the main musical genres of the last year?
2. Is there a link between a music’s duration and its popularity?
3. Do the biggest artists have loyal fans?

Website used for scraping:
https://www.last.fm

============================================================
6. PROJECT STRUCTURE
============================================================

final_project/
│
├── scraping/
│   ├── config.py
│   ├── utils.py
│   ├── scraper_genres.py
│   ├── scraper_artists.py
│   ├── scraper_albums.py
│   ├── scraper_tracks.py
│   ├── scraper_users.py
│   └── run_all.py
│
├── analysis/
│   ├── question1_genres_age.py
│   ├── question2_duration_popularity.py
│   ├── question3_loyal_fans.py
│   └── plots/
│
├── data/
│   ├── genres.csv
│   ├── artists.csv
│   ├── albums.csv
│   ├── tracks.csv
│   └── users.csv
│
└── README.txt


============================================================
7. DEPENDENCIES
============================================================

The project was developed with Python 3 and uses the following packages:

requests==2.31.0
beautifulsoup4==4.12.3
lxml==5.1.0
selenium==4.18.1
webdriver-manager==4.0.1
pandas==2.2.1
matplotlib==3.8.3
seaborn==0.13.2
numpy==1.26.4
scipy==1.12.0


============================================================
8. INSTALLATION
============================================================

Install the required packages with:

pip install -r requirements.txt

If there is issues with the requirements.txt file, we can install them manually with:

pip install requests==2.31.0 beautifulsoup4==4.12.3 lxml==5.1.0 selenium==4.18.1 webdriver-manager==4.0.1 pandas==2.2.1 matplotlib==3.8.3 seaborn==0.13.2 numpy==1.26.4 scipy==1.12.0


============================================================
9. RUNNING OF THE SCRAPING PHASE
============================================================

To run the full scraping pipeline, we go to the scraping folder and execute:

cd scraping
python run_all.py

This script launches the complete data collection process and generates the CSV
files for the different scraped resources.


============================================================
10. RUNNING OF THE ANALYSIS PHASE
============================================================

The analysis phase is divided into three separate scripts.

We go to the analysis folder and run each script manually:

cd analysis
python question1_genres_age.py
python question2_duration_popularity.py
python question3_loyal_fans.py

These scripts generate visualizations and print the main findings in the console.

The three analysis questions are:

Question 1:
What are the main musical genres of the last year?

Question 2:
Is there a link between a music’s duration and its popularity?

Question 3:
Do the biggest artists have loyal fans?


============================================================
11. OUTPUTS GENERATED
============================================================

Scraping output:
The scraping phase generates CSV files in the data/ folder:
- genres.csv
- artists.csv
- albums.csv
- tracks.csv
- users.csv

Analysis output:
The analysis scripts generate plots in:
analysis/plots/

Examples of generated PNG files include:
- q1_genres_by_artist_count.png
- q1_top_genres_by_listeners.png
- q1_top_genres_by_playcount.png
- q1_genre_reach_vs_engagement.png
- q1_loyalty_by_genre.png
- q2_duration_distribution.png
- q2_duration_vs_popularity_scatter.png
- q2_popularity_by_duration_boxplot.png
- q2_avg_popularity_by_duration.png
- q3_top_artists_loyalty.png
- q3_loyalty_vs_popularity.png
- q3_loyalty_by_tier.png
- q3_loyalty_by_genre.png


============================================================
12. VIDEO PRESENTATION
============================================================

Video link:
[INSERT LINK HERE]