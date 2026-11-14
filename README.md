# 🎬 Reel Insights – TMDB Movie Analytics

**What makes a movie earn – and what makes it loved?**

An end-to-end exploratory data analysis of **2,503 movies** from The Movie Database (TMDB), built across six linked tables
(movies, genres, cast, crew, keywords). The raw CSVs are cleaned with Pandas, loaded into a **MySQL** database, analysed with
**SQL** and **Pandas**, visualised with **Matplotlib/Seaborn**, and presented in an interactive **Streamlit** dashboard –
the **TMDB Master Dashboard**.

**Domain:** Media & Entertainment Analytics (box office / content analytics)

---

## 🔑 Top 5 insights

### 1. Money buys an audience, not quality
Budget and revenue are strongly linked (**correlation 0.68** – on average every extra $1 of budget goes with about $3 of revenue),
but budget has **no meaningful link to rating (−0.12)**. The best-rated movie, *The Shawshank Redemption* (8.73), is not a blockbuster.
*Evidence: Chart 5, Chart 8 (correlation heatmap), SQL Q3.*

### 2. Franchise blockbusters dominate the box office – but rate below average
**7 of the 10 highest-grossing movies** are Action + Adventure + Sci-Fi franchise films (*Avatar* $2.92B, *Avengers: Endgame* $2.80B).
**Adventure** has the highest average revenue (**~$400M**) yet is rated **below the 6.94 average**, while **War (7.36), History and Drama**
are rated highest but earn among the least – a clear commercial vs. critical trade-off.
*Evidence: SQL Q2, Q3, Q9; Charts 6, 6b, 6c.*

### 3. Animation is the sweet spot
**Animation** is the only genre that earns big **and** rates well: **~$375M** average revenue with a **7.20** rating.
Its average revenue grew **more than 6×** from the 1980s (~$77M) to the 2010s (~$485M).
*Evidence: Chart 6c, Chart 12 (genre × decade heatmap), Pandas Q7.*

### 4. Horror is the most cost-efficient genre
Horror has the **lowest median budget ($15M)** but earns more than Drama (median revenue $83M vs $77M) – several times its cost.
Low-budget horror (*Saw*, *Insidious*) appears among the **highest-ROI** films, despite Horror having the lowest average rating (6.62).
*Evidence: Pandas Q4, Chart 6b, Chart 9 (pairplot).*

### 5. Big budgets are risky – and the market is changing
**32% of above-average-budget movies earned below-average revenue** (273 movies, e.g. *The Marvels*: $275M budget → $206M).
Movie output **peaked in 2016 (121 movies)** and **halved in 2020 (52)** during the pandemic. Streaming originals
(*The Gray Man*, *The Irishman*) show tiny box office despite big budgets because they earn through subscriptions,
and new releases are **"trending" on popularity before votes build up**.
*Evidence: SQL Q7, Pandas Q5 & Q10, Chart 7.*

---

## 💡 Recommendations

| For | Recommendation |
|---|---|
| **Studios (box office)** | Put big budgets behind **existing IP** – franchises, sequels and adaptations ("based on novel", "sequel" are the top keywords) – because high budgets raise the ceiling but also the risk. |
| **Studios (best return per dollar)** | Use **low-budget horror** for reliable ROI, and invest in **animation / family** for revenue *and* reputation. |
| **Streaming platforms** | For a quality catalogue that keeps subscribers happy, license **well-rated, lower-cost genres** – Drama, War, History, Animation. |
| **Talent & casting** | Use track records: **Tom Hanks** (33 movies, 7.29 avg rating) combines output with quality; being prolific alone (Samuel L. Jackson, 39 movies, 6.94) does not guarantee higher ratings. |
| **Analysts** | Use **both** popularity (what is trending now) and vote count (reach over time) – they measure different things (correlation only 0.36). Treat streaming releases separately when judging box-office "flops". |

---

## 🧹 Key data decisions

- **Budget / revenue = 0 means *unknown*** (3.6% / 4.1% of movies). These values are **kept in the database**, **flagged**
  (`is_budget_missing`), and treated as missing only for money calculations – **never imputed**, because a filled-in budget would invent a fake profit and ROI.
- **Revenue below $10,000** (e.g. *The Emoji Movie* $216) is treated as a **data mistake**.
- **Runtime outliers** (IQR rule, outside 58.5–166.5 min) are **real films** (epics, specials) and are **kept**.
- **59 exact duplicate rows** removed; **0 orphaned rows**; 11 missing character names filled with `'Unknown'`.
- **Primary genre** = first genre listed, read from the CSV because a database table does not keep row order.
- People are counted by **`person_id`**, not name – 9 actor names belong to more than one person.

---

## 📁 Project structure
```
data/                     6 source CSVs (movies, genres, movie_genres, cast, crew, movie_keywords)
db.py                     MySQL connection helper – reads credentials from .env
.env.example              template for MySQL credentials (.env itself is never uploaded)
01_data_cleaning.ipynb    inspect & clean the 6 CSVs, load them into MySQL
02_sql_analysis.ipynb     10 SQL business questions + insights
queries.py                the same 10 SQL queries, reused by the dashboard's Query Explorer
03_pandas_analysis.ipynb  10 Pandas questions (profit, ROI, outliers, primary genre …) + insights
04_visualizations.ipynb   univariate / bivariate / multivariate charts + insights
TMDB_Master_Dashboard.py  Streamlit app "TMDB Master Dashboard"
requirements.txt          Python packages
```

## 🖥️ TMDB Master Dashboard (Streamlit)
| Page | What it does |
|---|---|
| **Home** | Project overview, headline numbers and key findings |
| **Filters** | Genre, release-year range, minimum rating and language – saved in `st.session_state` and applied on every page, with a live movie count |
| **Dashboard** | KPI cards (movies, genres, actors, average rating), top 10 movies by revenue, genre distribution, budget vs revenue, correlation heatmap, movies per year, and an automatic insight for the current filters |
| **Query Explorer** | Dropdown of the 10 SQL questions – runs the query live on MySQL and shows the table, a chart, the SQL and the insight |

## 🛠️ Tech stack
Python · Pandas · NumPy · MySQL · SQLAlchemy + PyMySQL · Matplotlib · Seaborn · Streamlit · streamlit-option-menu · Jupyter

---

## ▶️ How to run

**1. Set up the environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then put your MySQL password in .env
```

**2. Build the database** – requires a running **MySQL 8** server.
Run `01_data_cleaning.ipynb` first: it creates the `tmdb` database and loads all six tables.

**3. Run the notebooks** `02` → `04` in order (Run All).

**4. Start the dashboard**
```bash
streamlit run TMDB_Master_Dashboard.py
```
