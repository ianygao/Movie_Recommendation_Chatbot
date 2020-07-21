from math import sqrt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def train(movies):
    global df_movies, cosine_sim_movies
    # Reading ratings file
    # ratings = pd.read_csv('ratings.csv', sep=',', encoding='latin-1',
    #                       usecols=['userId', 'movieId', 'rating', 'timestamp'])
    # Reading movies file
    if movies is None:
        movies = pd.read_csv('movies.csv', sep=',', encoding='latin-1', usecols=['movieId', 'title', 'genres'])
    df_movies = movies
    # Define a TF-IDF Vectorizer Object.
    tfidf_movies_genres = TfidfVectorizer(token_pattern='[a-zA-Z0-9\-]+')
    # Replace NaN with an empty string
    df_movies['genres'] = df_movies['genres'].replace(to_replace="(no genres listed)", value="")
    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_movies_genres_matrix = tfidf_movies_genres.fit_transform(df_movies['genres'])
    # Compute the cosine similarity matrix
    cosine_sim_movies = linear_kernel(tfidf_movies_genres_matrix, tfidf_movies_genres_matrix)
    return df_movies, cosine_sim_movies


# train(None)


def get_recommendations_based_on_genres(movie_title, cosine_sim_movies):
    """
    Calculates top 2 movies to recommend based on given movie titles genres.
    :param movie_title: title of movie to be taken for base of recommendation
    :param cosine_sim_movies: cosine similarity between movies
    :return: Titles of movies recommended to user
    """
    # Get the index of the movie that matches the title
    idx_movie = df_movies.loc[df_movies['title'].isin([movie_title])]
    idx_movie = idx_movie.index

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores_movies = list(enumerate(cosine_sim_movies[idx_movie][0]))

    # Sort the movies based on the similarity scores
    sim_scores_movies = sorted(sim_scores_movies, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores_movies = sim_scores_movies[0:10]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores_movies if not i[0] == idx_movie]

    # Return the top 1 most similar movies
    return df_movies['title'].iloc[movie_indices[0]]


# my_movie = input("Enter the name and the year of the movie, forexample, Toy Story (1995):")
#
# recommend_to_watch = get_recommendations_based_on_genres(my_movie)
# print("Based on " + my_movie + ", " + "we recommend you to watch " + recommend_to_watch + ".")
