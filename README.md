# Reel Insights – TMDB Movie Analytics

End-to-end EDA of ~2,500 TMDB movies: data cleaning → SQL (MySQL) → Pandas analysis → visualizations → Streamlit app.

## Project structure
```
data/                     6 source CSVs
db.py                     MySQL connection helper (reads .env)
.env.example              template for MySQL credentials
01_data_cleaning.ipynb    clean CSVs and load into MySQL
02_sql_analysis.ipynb     10 SQL questions
queries.py                the 10 SQL queries, reused by the Streamlit Query Explorer
03_pandas_analysis.ipynb  10 Pandas questions
04_visualizations.ipynb   univariate / bivariate / multivariate charts
TMDB_Master_Dashboard.py  Streamlit app (Filters, Dashboard, Query Explorer)
```

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then put your MySQL password in .env
```
Requires a running MySQL 8 server. Run `01_data_cleaning.ipynb` first – it creates the `tmdb` database and loads all tables.

## Run the app
```bash
streamlit run TMDB_Master_Dashboard.py
```

## Top 5 insights
_To be filled in after the analysis._
