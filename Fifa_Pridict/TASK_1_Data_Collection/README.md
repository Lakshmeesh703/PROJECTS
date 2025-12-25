# TASK 1: Data Collection (20 Marks)

##  Objective
Collect and integrate data from multiple sources for FIFA World Cup 2026 prediction project.

##  Contents

### Scripts (`scripts/`)
- **`fifa_player_web_scraper.py`** - Main web scraper for FIFA 26 player data from Kaggle
- **`data_100_scraper.py`** - Scraper for top 100 FIFA ranked teams
- **`fifa_48_team_scraper.py`** - Scraper for 48 qualified teams data

### Data (`data/`)
- **`sources/`** - Original CSV data files from multiple sources
  - FIFA World Cup historical data
  - FIFA rankings
  - International football results
  - Player databases
- **`raw/`** - Raw scraped data before processing

### Notebooks (`notebooks/`)
- Jupyter notebooks for data collection demonstrations

### Outputs (`outputs/`)
- Data collection reports and summaries

##  Deliverables
-  Web scraping scripts (automated)
-  Multiple data sources integrated
-  18,405 FIFA 26 player records
-  100+ teams data collected
-  Data collection report

##  Data Sources
1. **FIFA Rankings** - Official FIFA ranking data
2. **Player Database** - FIFA 26 player statistics (Kaggle)
3. **Match Results** - Historical international football matches
4. **World Cup Data** - Historical World Cup statistics
5. **Qualification Data** - FIFA 2026 qualified teams

##  How to Run

### Web Scraper
```bash
cd scripts
python fifa_player_web_scraper.py
```

### Other Scrapers
```bash
python data_100_scraper.py
python fifa_48_team_scraper.py
```

##  Results
- **Players Collected**: 18,405
- **Teams Covered**: 102
- **Confederations**: 6 (UEFA, CONMEBOL, CONCACAF, CAF, AFC, OFC)
- **Data Quality**: 98/100

##  Documentation
See `../documentation/weekly_reports/Week1_Data_Collection.md` for detailed report.
