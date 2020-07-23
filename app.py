# doing necessary imports
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests
import pymongo
import pandas as pd
import json
import os
import logging
from pymongo import MongoClient
from models import ContentBasedFiltering
from models import ItemBasedCollaborativeFiltering

app = Flask(__name__)  # initialising the flask app with the name 'app'


@app.before_first_request
def startup():
    global df_movies, cosine_sim_movies, ratings_df, movie_matrix_UII
    # init content-based model
    movies = pd.read_csv('data/movies.csv', sep=',', encoding='latin-1', usecols=['movieId', 'title', 'genres'])
    df_movies, cosine_sim_movies = ContentBasedFiltering.train(movies)
    # init item-based model
    u_data = pd.read_csv('data/u.data', sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
    movie_titles = pd.read_csv('data/Movie_Titles.csv', encoding='unicode_escape')
    ratings_df, movie_matrix_UII = ItemBasedCollaborativeFiltering.train(u_data, movie_titles)
    print("before_first_request Test success!")
    logging.info("before_first_request Test success!")


# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")
    movie_name = parameters.get("movie_name")
    cust_contact = parameters.get("cust_contact")
    cust_email = parameters.get("cust_email")
    if intent == 'movie_language':
        return {
            "fulfillmentText": "Test success! Intent: movie_language",
        }
    elif intent == 'ContentBasedRecommendation':
        rcmd_movies = ContentBasedFiltering.get_recommendations_based_on_genres(movie_name)
        webhookresponse = "We recommend you to watch: \n" + rcmd_movies + "\n"
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]
                    }
                },
                {
                    "text": {
                        "text": [
                            "The above are the recommendations based on the genres. Would you also like me to recommend you some movies based on the rating? Type.. \n Yes \n No "
                        ]
                    }
                }
            ]
        }
    elif intent == 'ItemBasedRecommendation':
        rcmd_movies = ItemBasedCollaborativeFiltering.get_recommendations_based_on_rating(movie_name)
        webhookresponse = "We recommend you to watch: \n" + rcmd_movies
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                }
            ]
        }
    return {
        "fulfillmentText": "Test success! Default response",
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
# if __name__ == "__main__":
#     app.run(port=5000, debug=True)  # running the app on the local machine on port 8000
