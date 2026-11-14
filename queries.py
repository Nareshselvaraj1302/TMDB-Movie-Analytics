"""The 10 SQL questions from 02_sql_analysis.ipynb - used by the Streamlit Query Explorer (TMDB_Master_Dashboard.py)."""

q1 = '''
SELECT m.title,
       m.release_date
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g        ON mg.genre_id = g.genre_id
WHERE g.genre_name = 'Action'
  AND YEAR(m.release_date) > 2015
ORDER BY m.release_date
'''

q2 = '''
SELECT m.title,
       ROUND(m.revenue / 1000000, 1) AS revenue_musd,
       GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g        ON mg.genre_id = g.genre_id
GROUP BY m.movie_id, m.title, m.revenue
ORDER BY m.revenue DESC
LIMIT 10
'''

q3 = '''
SELECT g.genre_name,
       COUNT(*)                                      AS movie_count,
       ROUND(AVG(NULLIF(m.budget, 0))  / 1000000, 1) AS avg_budget_musd,
       ROUND(AVG(NULLIF(m.revenue, 0)) / 1000000, 1) AS avg_revenue_musd
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g        ON mg.genre_id = g.genre_id
GROUP BY g.genre_name
ORDER BY avg_revenue_musd DESC
'''

q4 = '''
SELECT c.actor_name,
       COUNT(DISTINCT c.movie_id) AS movie_count
FROM `cast` c
GROUP BY c.person_id, c.actor_name
ORDER BY movie_count DESC
LIMIT 10
'''

q5 = '''
SELECT cr.person_name AS director,
       COUNT(DISTINCT cr.movie_id) AS movie_count
FROM crew cr
WHERE cr.job = 'Director'
GROUP BY cr.person_id, cr.person_name
HAVING COUNT(DISTINCT cr.movie_id) > 3
ORDER BY movie_count DESC, director
'''

q6 = '''
SELECT mk.keyword_name,
       COUNT(DISTINCT mk.movie_id) AS movie_count
FROM movie_keywords mk
GROUP BY mk.keyword_id, mk.keyword_name
ORDER BY movie_count DESC
LIMIT 10
'''

q7 = '''
SELECT m.title,
       ROUND(m.budget  / 1000000, 1) AS budget_musd,
       ROUND(m.revenue / 1000000, 1) AS revenue_musd
FROM movies m
WHERE m.revenue > 0
  AND m.budget  > (SELECT AVG(budget)  FROM movies WHERE budget  > 0)
  AND m.revenue < (SELECT AVG(revenue) FROM movies WHERE revenue > 0)
ORDER BY m.budget DESC
'''

q8 = '''
SELECT c.actor_name,
       COUNT(DISTINCT c.movie_id) AS nolan_movies
FROM `cast` c
JOIN crew cr ON c.movie_id = cr.movie_id
WHERE cr.job = 'Director'
  AND cr.person_name = 'Christopher Nolan'
GROUP BY c.person_id, c.actor_name
ORDER BY nolan_movies DESC, c.actor_name
'''

q9 = '''
SELECT g.genre_name,
       COUNT(DISTINCT m.movie_id)  AS movie_count,
       ROUND(AVG(m.vote_average), 2) AS avg_rating
FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g        ON mg.genre_id = g.genre_id
GROUP BY g.genre_name
HAVING COUNT(DISTINCT m.movie_id) >= 20
ORDER BY avg_rating DESC
'''

q10 = '''
SELECT m.title,
       COUNT(mk.keyword_id) AS keyword_count,
       ROUND(m.popularity, 1) AS popularity
FROM movies m
JOIN movie_keywords mk ON m.movie_id = mk.movie_id
GROUP BY m.movie_id, m.title, m.popularity
ORDER BY keyword_count DESC
LIMIT 10
'''

SQL_QUERIES = {
    'List all movies in the Action genre released after 2015, showing title and release date.': q1,
    'Find the top 10 highest-grossing movies along with the genre(s) each belongs to.': q2,
    'Calculate the average budget and average revenue for each genre, sorted by average revenue descending.': q3,
    'List the top 10 actors who have appeared in the most movies in the dataset.': q4,
    'Find all directors who have directed more than 3 movies, along with their movie count.': q5,
    'List the top 10 most frequently used keywords across all movies.': q6,
    'Find movies where the budget was above the overall average budget but the revenue was below the overall average revenue.': q7,
    'List all actors who have appeared in a movie directed by a specific director (e.g., Christopher Nolan).': q8,
    'Find the genre with the highest average rating, considering only genres with at least 20 movies.': q9,
    'List the top 10 movies with the highest number of keywords tagged to them.': q10,
}
