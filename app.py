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

app = Flask(__name__)  # initialising the flask app with the name 'app'


@app.before_first_request
def startup():
    global df_movies, cosine_sim_movies
    movies = pd.read_csv('models/movies.csv', sep=',', encoding='latin-1', usecols=['movieId', 'title', 'genres'])
    df_movies, cosine_sim_movies = ContentBasedFiltering.train(movies)
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
    elif intent == 'ProcessRecommendation':
        rcmd_movie = ContentBasedFiltering.get_recommendations_based_on_genres(movie_name, cosine_sim_movies)
        webhookresponse = "we recommend you to watch " + rcmd_movie + "."
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                }
                # {
                #     "text": {
                #         "text": [
                #             "Do you want me to send the detailed report to your e-mail address? Type.. \n 1. Sure \n 2. Not now "
                #             # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                #         ]
                #
                #     }
                # }
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
