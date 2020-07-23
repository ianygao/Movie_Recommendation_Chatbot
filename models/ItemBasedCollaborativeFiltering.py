import pandas as pd


def train(u_data, movie_titles):
    global ratings_df, movie_matrix_UII
    if u_data is None:
        movie_data_df = pd.read_csv('../data/u.data', sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
    else:
        movie_data_df = u_data
    # here we are adding the movie title and joining with the main data
    if movie_titles is None:
        movie_titles = pd.read_csv('../data/Movie_Titles.csv', encoding='unicode_escape')
    movie_data_df = pd.merge(movie_data_df, movie_titles, on='movie_id')
    # creating mean rating data to capture the mean rating for all movies
    ratings_df = pd.DataFrame(movie_data_df.groupby('title')['rating'].mean())
    # creating number of rating data
    # how many the movie has been rated
    ratings_df['number_of_ratings'] = pd.DataFrame(movie_data_df.groupby('title')['rating'].count())
    # creating user-item interaction matrix
    # to find the relation between individual users and individual movies
    # NaN=0 means no rating entries
    movie_matrix_UII = movie_data_df.pivot_table(index='user_id', columns='title', values='rating').fillna(0)
    # Most rated movies
    ratings_df.sort_values('number_of_ratings', ascending=False).head(10)
    return ratings_df, movie_matrix_UII


# train(None, None)


def get_recommendations_based_on_rating(movie_title):
    # Making recommendation
    # Fetching rating for specified movie name
    movie_user_rating = movie_matrix_UII[movie_title]
    # Finding the correlation with different movies (on the similar rating)
    similar_to_movie_user_rating = movie_matrix_UII.corrwith(movie_user_rating)
    # Making the most meaningful recommendation
    correlation_movie_user_rating = pd.DataFrame(similar_to_movie_user_rating, columns=['Correlation with user rating'])
    correlation_movie_user_rating.dropna(inplace=True)
    correlation_movie_user_rating = correlation_movie_user_rating.join(ratings_df['number_of_ratings'])
    result_df = correlation_movie_user_rating[correlation_movie_user_rating['number_of_ratings'] > 20].sort_values(
        by='Correlation with user rating', ascending=False).head(6)
    # obtain data from the second row(filter out the same movie)
    result = result_df.iloc[1:, 0].keys().tolist()
    result_str = ''
    for i in result:
        result_str += i + '\n'
    print(result_str)
    # Return the top 5 most similar movies
    return result_str


# get_recommendations_based_on_rating('Toy Story (1995)')
