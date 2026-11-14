# ============================================================
#  TMDB Master Dashboard  -  Reel Insights project (Streamlit)
#  Run:  streamlit run TMDB_Master_Dashboard.py
# ============================================================
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine

import os
from urllib.parse import quote_plus
import db                                   # loads MYSQL_USER, MYSQL_PASSWORD ... from .env
from queries import SQL_QUERIES             # the 10 SQL questions from notebook 02

st.set_page_config(page_title='TMDB Master Dashboard', page_icon='🎬', layout='wide')
sns.set_theme(style='whitegrid')

# ------------------------------------------------------------
# Connect to sql (same format as the TMDB reference code)
# ------------------------------------------------------------
password = quote_plus(os.getenv('MYSQL_PASSWORD'))
engine = create_engine(f"mysql+pymysql://root:{password}@localhost:3306/tmdb")

DATA_DIR = Path(__file__).parent / 'data'

# One fixed colour per genre - the same colours as notebook 04
GENRE_COLORS = {'Action': '#d62728', 'Drama': '#1f77b4', 'Comedy': '#ff7f0e',
                'Adventure': '#2ca02c', 'Horror': '#7f3c8d', 'Other': '#c7c7c7'}

# Language codes -> readable names for the language dropdown
LANGUAGE_NAMES = {'en': 'English', 'ja': 'Japanese', 'fr': 'French', 'it': 'Italian', 'es': 'Spanish',
                  'de': 'German', 'ko': 'Korean', 'cn': 'Cantonese', 'sv': 'Swedish', 'pt': 'Portuguese',
                  'da': 'Danish', 'hi': 'Hindi', 'id': 'Indonesian', 'zh': 'Mandarin', 'pl': 'Polish',
                  'tr': 'Turkish', 'lv': 'Latvian', 'fi': 'Finnish', 'el': 'Greek', 'ru': 'Russian', 'sr': 'Serbian'}


# ------------------------------------------------------------
# Load the data from MySQL (cached - read once, not on every click)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    movies = pd.read_sql("select * from movies", con=engine)
    genres = pd.read_sql("select * from genres", con=engine)
    movie_genres = pd.read_sql("select * from movie_genres", con=engine)
    cast = pd.read_sql("select movie_id, person_id from `cast`", con=engine)

    # Same preparation as notebooks 03 and 04
    movies['release_date'] = pd.to_datetime(movies['release_date'])
    movies['release_year'] = movies['release_date'].dt.year
    movies['budget'] = movies['budget'].replace(0, np.nan)              # 0 = unknown
    movies.loc[movies['revenue'] < 10000, 'revenue'] = np.nan           # 0 and mistakes = unknown
    movies['budget_musd'] = movies['budget'] / 1000000
    movies['revenue_musd'] = movies['revenue'] / 1000000
    movies['language'] = movies['original_language'].map(LANGUAGE_NAMES).fillna(movies['original_language'])

    # Primary genre = first genre listed (from the CSV - MySQL does not keep the order)
    genre_order = pd.read_csv(DATA_DIR / 'movie_genres.csv').drop_duplicates()
    primary = genre_order.drop_duplicates(subset='movie_id', keep='first')
    primary = pd.merge(primary, genres, on='genre_id').rename(columns={'genre_name': 'primary_genre'})
    movies = pd.merge(movies, primary[['movie_id', 'primary_genre']], on='movie_id', how='left')

    # All genres of every movie (one row per movie per genre)
    movie_genre_names = pd.merge(movie_genres, genres, on='genre_id')
    return movies, movie_genre_names, cast


movies, movie_genre_names, cast = load_data()

ALL_GENRES = sorted(movie_genre_names['genre_name'].unique())
ALL_LANGUAGES = ['All languages'] + movies['language'].value_counts().index.tolist()
MIN_YEAR, MAX_YEAR = int(movies['release_year'].min()), int(movies['release_year'].max())
OVERALL_RATING = movies['vote_average'].mean()

# ------------------------------------------------------------
# Filter values live in st.session_state so they stay the same on every page
# ------------------------------------------------------------
DEFAULT_FILTERS = {
    'f_genres': [],                          # empty = all genres
    'f_years': (MIN_YEAR, MAX_YEAR),
    'f_min_rating': 0.0,
    'f_language': 'All languages',
}
for key, value in DEFAULT_FILTERS.items():
    if key not in st.session_state:
        st.session_state[key] = value
    # Re-assign every run: keeps the values when the Filters page is not on screen
    st.session_state[key] = st.session_state[key]


def get_filtered_movies():
    """Return only the movies that match the current filters."""
    df = movies.copy()
    if st.session_state.f_genres:
        ids = movie_genre_names[movie_genre_names['genre_name'].isin(st.session_state.f_genres)]['movie_id']
        df = df[df['movie_id'].isin(ids)]
    start_year, end_year = st.session_state.f_years
    df = df[(df['release_year'] >= start_year) & (df['release_year'] <= end_year)]
    df = df[df['vote_average'] >= st.session_state.f_min_rating]
    if st.session_state.f_language != 'All languages':
        df = df[df['language'] == st.session_state.f_language]
    return df


filtered = get_filtered_movies()

# ------------------------------------------------------------
# Sidebar menu (option_menu, as in the reference code)
# ------------------------------------------------------------
with st.sidebar:
    selected = option_menu('TMDB Master Dashboard', ['Home', 'Filters', 'Dashboard', 'Query Explorer'],
                           icons=['house', 'funnel', 'bar-chart', 'search'], menu_icon='film', default_index=0)

    st.markdown('**Active filters**')
    st.caption(f"Genres: {', '.join(st.session_state.f_genres) if st.session_state.f_genres else 'All'}")
    st.caption(f"Years: {st.session_state.f_years[0]} – {st.session_state.f_years[1]}")
    st.caption(f"Min rating: {st.session_state.f_min_rating}")
    st.caption(f"Language: {st.session_state.f_language}")
    st.metric('Movies matching', f'{len(filtered):,}')


# ============================================================
# PAGE: HOME
# ============================================================
if selected == 'Home':
    st.title('🎬 TMDB Master Dashboard')
    st.markdown('### Reel Insights – what makes a movie earn, and what makes it loved?')
    st.write('An end-to-end analysis of **~2,500 movies** from The Movie Database (TMDB): '
             'data cleaning, SQL, Pandas analysis and visualisation – all reading from a MySQL database.')

    k1, k2, k3, k4 = st.columns(4)
    k1.metric('Movies', f"{movies['movie_id'].nunique():,}")
    k2.metric('Genres', len(ALL_GENRES))
    k3.metric('Actors', f"{cast['person_id'].nunique():,}")
    k4.metric('Years covered', f'{MAX_YEAR - MIN_YEAR + 1}', help=f'Release years {MIN_YEAR} to {MAX_YEAR}')

    st.subheader('How to use this dashboard', divider='rainbow')
    st.markdown("""
1. **Filters** – choose genres, years, minimum rating and language. Your choice is remembered on every page.
2. **Dashboard** – KPI cards and charts for the movies that match your filters.
3. **Query Explorer** – run the 10 SQL business questions and see the table, a chart and the insight.
""")

    st.subheader('Key findings', divider='rainbow')
    st.markdown("""
- 💰 **Money buys an audience, not quality** – budget ↔ revenue correlation is **0.68**, budget ↔ rating only **−0.12**.
- 🏆 **Franchise blockbusters rule the box office** – 7 of the top 10 grossing films are Action/Adventure/Sci-Fi franchises.
- 🎨 **Animation is the sweet spot** – the only genre that earns big (~$375M average) *and* rates well (7.20).
- 👻 **Horror is the most cost-efficient** – lowest median budget ($15M), earns several times its cost.
- 📉 **2020 was a shock** – movie output halved in the pandemic year (121 movies in 2016 → 52 in 2020).
""")


# ============================================================
# PAGE: FILTERS
# ============================================================
if selected == 'Filters':
    st.title('Filters')
    st.write('Set your filters here – they apply to the **Dashboard** and are shown in the sidebar on every page.')

    c1, c2, c3 = st.columns([0.45, 0.1, 0.45])
    with c1:
        st.subheader('What', divider='rainbow')
        st.multiselect('Genre (leave empty for all genres)', ALL_GENRES, key='f_genres')
        st.selectbox('Original language', ALL_LANGUAGES, key='f_language')
    with c3:
        st.subheader('When & how good', divider='rainbow')
        st.slider('Release year range', MIN_YEAR, MAX_YEAR, key='f_years')
        st.slider('Minimum average rating', 0.0, 10.0, step=0.1, key='f_min_rating')

    st.divider()
    filtered = get_filtered_movies()           # recalculate with the new values
    m1, m2 = st.columns(2)
    m1.metric('Movies matching your filters', f'{len(filtered):,}',
              delta=f'{len(filtered) - len(movies):,} vs all movies', delta_color='off')
    m2.metric('Share of all movies', f'{len(filtered) / len(movies) * 100:.1f}%')

    if st.button('Reset all filters'):
        for key, value in DEFAULT_FILTERS.items():
            del st.session_state[key]
        st.rerun()

    if len(filtered) > 0:
        st.caption('Preview of the matching movies (highest rated first)')
        st.dataframe(filtered.sort_values('vote_average', ascending=False)
                     [['title', 'release_year', 'language', 'primary_genre', 'vote_average', 'revenue_musd']]
                     .rename(columns={'release_year': 'year', 'primary_genre': 'primary genre',
                                      'vote_average': 'rating', 'revenue_musd': 'revenue ($M)'}),
                     hide_index=True, height=300)


# ============================================================
# PAGE: DASHBOARD
# ============================================================
if selected == 'Dashboard':
    st.title('Dashboard')

    if len(filtered) == 0:
        st.warning('No movies match the current filters. Go to **Filters** and widen your selection.')
        st.stop()

    # ---------------- KPI cards ----------------
    filtered_genres = movie_genre_names[movie_genre_names['movie_id'].isin(filtered['movie_id'])]
    filtered_cast = cast[cast['movie_id'].isin(filtered['movie_id'])]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric('Total movies', f'{len(filtered):,}', border=True)
    k2.metric('Genres represented', filtered_genres['genre_name'].nunique(), border=True)
    k3.metric('Total actors', f"{filtered_cast['person_id'].nunique():,}", border=True)
    k4.metric('Average rating', f"{filtered['vote_average'].mean():.2f}",
              delta=f"{filtered['vote_average'].mean() - OVERALL_RATING:+.2f} vs all movies", border=True)

    # ---------------- Row 1: top 10 revenue + genre distribution ----------------
    c1, c2, c3 = st.columns([0.45, 0.1, 0.45])
    with c1:
        st.subheader('Top 10 movies by revenue', divider='rainbow')
        top10 = filtered.dropna(subset=['revenue_musd']).sort_values('revenue_musd', ascending=False).head(10)
        if len(top10) > 0:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(data=top10, x='revenue_musd', y='title', color='steelblue', ax=ax)
            ax.set_xlabel('Revenue (million USD)')
            ax.set_ylabel('')
            st.pyplot(fig)
        else:
            st.info('No known revenue values for this selection.')

    with c3:
        st.subheader('Genre distribution', divider='rainbow')
        genre_counts = filtered_genres['genre_name'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(x=genre_counts.values, y=genre_counts.index, color='mediumseagreen', ax=ax)
        ax.set_xlabel('Number of movies (a movie counts once in each of its genres)')
        ax.set_ylabel('')
        st.pyplot(fig)

    # ---------------- Row 2: budget vs revenue + insight ----------------
    c1, c2, c3 = st.columns([0.45, 0.1, 0.45])
    with c1:
        st.subheader('Budget vs revenue', divider='rainbow')
        money = filtered.dropna(subset=['budget_musd', 'revenue_musd']).copy()
        if len(money) > 0:
            # Colour the 5 main primary genres, everything else grey
            money['genre_group'] = money['primary_genre'].where(money['primary_genre'].isin(GENRE_COLORS), 'Other')
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.scatterplot(data=money, x='budget_musd', y='revenue_musd', hue='genre_group',
                            palette=GENRE_COLORS, alpha=0.6, ax=ax)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Budget (million USD, log scale)')
            ax.set_ylabel('Revenue (million USD, log scale)')
            ax.legend(title='Primary genre')
            st.pyplot(fig)
            st.caption(f'{len(money):,} movies with both budget and revenue known '
                       f'({len(filtered) - len(money):,} with unknown values are not shown).')
        else:
            st.info('No movies with both budget and revenue known in this selection.')

    with c3:
        st.subheader('Insight for this selection', divider='rainbow')
        genre_money = pd.merge(filtered_genres, filtered[['movie_id', 'revenue_musd', 'vote_average']], on='movie_id')
        genre_summary = genre_money.groupby('genre_name').agg(avg_revenue=('revenue_musd', 'mean'),
                                                              avg_rating=('vote_average', 'mean'),
                                                              movies=('movie_id', 'nunique'))
        genre_summary = genre_summary[genre_summary['movies'] >= 5].dropna()

        lines = [f"- **{len(filtered):,} movies** match your filters, with an average rating of "
                 f"**{filtered['vote_average'].mean():.2f}** "
                 f"({'above' if filtered['vote_average'].mean() >= OVERALL_RATING else 'below'} the overall 6.94)."]
        if len(top10) > 0:
            best = top10.iloc[0]
            lines.append(f"- The **highest-grossing movie** is **{best['title']}** ({best['release_year']}) "
                         f"with **${best['revenue_musd']:,.0f}M**.")
        if len(genre_summary) > 0:
            top_genre = genre_summary['avg_revenue'].idxmax()
            best_rated = genre_summary['avg_rating'].idxmax()
            lines.append(f"- The **highest-grossing genre** in this selection is **{top_genre}** "
                         f"(average **${genre_summary.loc[top_genre, 'avg_revenue']:,.0f}M**).")
            lines.append(f"- The **best-rated genre** is **{best_rated}** "
                         f"(average **{genre_summary.loc[best_rated, 'avg_rating']:.2f}**).")
        if len(money) > 2:
            lines.append(f"- Budget and revenue correlation here: **{money['budget'].corr(money['revenue']):.2f}** "
                         f"(0.68 for all movies).")
        st.info('\n'.join(lines))

    # ---------------- Row 3: the two charts from the reference code (sample_streamlit.py) ----------------
    c1, c2, c3 = st.columns([0.45, 0.1, 0.45])
    # Heat map
    with c1:
        st.subheader('Correlation Heatmap', divider='rainbow')
        num_cols = ['budget', 'revenue', 'runtime', 'popularity', 'vote_average', 'vote_count']

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered[num_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)

        st.pyplot(fig)
    with c3:
        st.subheader("Movies Released per Year", divider='rainbow')

        movies_per_year = filtered.groupby(filtered["release_date"].dt.year).size()

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(movies_per_year.index, movies_per_year.values)

        ax.set_xlabel("Year")
        ax.set_ylabel("Number of Movies")

        st.pyplot(fig)


# ============================================================
# PAGE: QUERY EXPLORER
# ============================================================
# Chart settings for each saved query: chart type, columns, and the insight from notebook 02
QUERY_CHARTS = [
    {'kind': 'year_count', 'x': 'release_date', 'y': None, 'label': 'Number of Action movies',
     'insight': '268 Action movies were released after 2015. Output peaked in 2016 and 2018 (39 each) and dropped to 22 in 2020, '
                'the pandemic year. Low counts for 2025–2026 reflect partial data, not a decline.'},
    {'kind': 'barh', 'x': 'revenue_musd', 'y': 'title', 'label': 'Revenue (million USD)',
     'insight': '7 of the 10 highest-grossing movies are Action + Adventure + Science Fiction franchise films, all above $1.9 billion. '
                'Big franchise spectacle and family animation are the most reliable routes to billion-dollar box office.'},
    {'kind': 'barh', 'x': 'avg_revenue_musd', 'y': 'genre_name', 'label': 'Average revenue (million USD)',
     'insight': 'Adventure earns the highest average revenue (~$400M on a ~$111M budget). Horror has the smallest budget (~$26M) '
                'but earns about 4× its cost. Drama is the most common genre yet earns among the least.'},
    {'kind': 'barh', 'x': 'movie_count', 'y': 'actor_name', 'label': 'Number of movies',
     'insight': 'Samuel L. Jackson leads with 39 movies, followed by Robert De Niro and Brad Pitt (38 each). '
                'The list mixes franchise stars with long-career character actors – both proven, bankable choices.'},
    {'kind': 'barh', 'x': 'movie_count', 'y': 'director', 'label': 'Number of movies directed', 'top': 15,
     'insight': '217 directors have directed more than 3 movies. Steven Spielberg leads clearly with 27, ahead of Ridley Scott '
                'and Tim Burton (19 each). Long track records help studios judge commercial risk.'},
    {'kind': 'barh', 'x': 'movie_count', 'y': 'keyword_name', 'label': 'Number of movies',
     'insight': 'Existing stories dominate: "based on novel or book", "sequel", "based on true story" and "based on comic" are all '
                'in the top 10. Studios clearly prefer proven material over original ideas.'},
    {'kind': 'scatter', 'x': 'budget_musd', 'y': 'revenue_musd', 'label': None,
     'insight': '273 movies (32% of above-average-budget films) cost more than the average budget (~$61M) but earned less than the '
                'average revenue (~$223M). Some, like The Gray Man, are streaming releases with almost no cinema run – not real flops.'},
    {'kind': 'barh', 'x': 'nolan_movies', 'y': 'actor_name', 'label': 'Number of Nolan films', 'top': 15,
     'insight': '84 actors have appeared in Christopher Nolan\'s 11 films. Michael Caine (6), Cillian Murphy (5) and Christian Bale (4) '
                'lead – Nolan works with a trusted core group plus new faces for each film.'},
    {'kind': 'barh_rating', 'x': 'avg_rating', 'y': 'genre_name', 'label': 'Average rating (axis starts at 6)',
     'insight': 'War has the highest average rating (7.36), then History and Music. Horror (6.62) and Action (6.73) rate lowest. '
                'The top-earning genres rate below the 6.94 average – a commercial vs critical trade-off.'},
    {'kind': 'barh', 'x': 'keyword_count', 'y': 'title', 'label': 'Number of keywords',
     'insight': 'Smile 2 has by far the most keywords (98); a typical movie has about 16. Keyword count is not linked to popularity '
                '(correlation 0.09) – it reflects how thoroughly users tagged a film, not its success.'},
]
QUESTION_LIST = list(SQL_QUERIES.keys())

if selected == 'Query Explorer':
    st.title('Query Explorer')
    st.write('Pick one of the 10 SQL business questions. The query runs live on the MySQL database.')

    option = st.selectbox('Select a query', QUESTION_LIST,
                          format_func=lambda q: f'Q{QUESTION_LIST.index(q) + 1}. {q}')
    number = QUESTION_LIST.index(option)
    chart = QUERY_CHARTS[number]

    df = pd.read_sql(SQL_QUERIES[option], con=engine)

    with st.expander('Show the SQL query'):
        st.code(SQL_QUERIES[option].strip(), language='sql')

    c1, c2, c3 = st.columns([0.45, 0.1, 0.45])
    with c1:
        st.subheader('Result', divider='rainbow')
        st.caption(f'{len(df):,} rows')
        st.dataframe(df, hide_index=True, height=450)

    with c3:
        st.subheader('Chart', divider='rainbow')
        fig, ax = plt.subplots(figsize=(8, 6))

        if chart['kind'] == 'year_count':
            per_year = pd.to_datetime(df['release_date']).dt.year.value_counts().sort_index()
            ax.bar(per_year.index.astype(str), per_year.values, color='steelblue')
            ax.set_xlabel('Release year')
            ax.set_ylabel(chart['label'])

        elif chart['kind'] == 'scatter':
            sns.scatterplot(data=df, x=chart['x'], y=chart['y'], alpha=0.6, ax=ax)
            ax.set_xlabel('Budget (million USD)')
            ax.set_ylabel('Revenue (million USD)')

        else:   # horizontal bar charts
            plot_df = df.dropna(subset=[chart['x']]).head(chart.get('top', 10))
            sns.barplot(data=plot_df, x=chart['x'], y=chart['y'], color='steelblue', ax=ax)
            if chart['kind'] == 'barh_rating':
                ax.set_xlim(6, 7.5)
                ax.axvline(OVERALL_RATING, color='red', linestyle='--', label='Overall average (6.94)')
                ax.legend()
            ax.set_xlabel(chart['label'])
            ax.set_ylabel('')

        st.pyplot(fig)

    st.subheader('Insight', divider='rainbow')
    st.info(chart['insight'])
