#!/usr/bin/python3
from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import HTTPException

from fetcher.fetcher import Fetcher
from curator.curator import Curator
from summarizer.summarizer import Summarizer

import json
import sys
import argparse

import pprint
import traceback
import time

# initialise all the stuff
fetcher = Fetcher()
curator = Curator()
summarizer = Summarizer()

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, Home!"

@app.errorhandler(404)
def not_found(error):
    print(request)
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(Exception)
def handle_error(e):
    tb = traceback.format_exc()
    print(tb)
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

@app.route('/api/v1.0/newsfeed/get', methods=['GET'])
def get_newsfeed():
    #cluster = request.args.get('title')

    articles = fetcher.simple_fetch()
    result = curator.curate(articles, use_cluster=False)

    print(result)
    return jsonify(result)

@app.route('/api/v1.0/newsfeed/get_article_summary', methods=['POST'])
def get_article_summary():
    #title = request.args.get('title')
    #link = request.args.get('link')
    print('got a request')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(request.data)
    #pp.pprint(request.values)
    print('hello ' , request.json['articles'][0])
    articles = request.get_json()['articles']
    print(articles)

    #print('got params ', title, link)
    print('got request')
    #print("AAAAAAAAAAAAAAAAAAAAAAA ", type(articles), articles)
    t00 = time.time()
    t0 = time.time()
    print("[{}] starting ".format(time.time()-t0), file=sys.stderr); t0 = time.time();
    filled = []
    if articles is not None:
        for article in articles:
            if article['url'] is not None:
            #title is not None and link is not None:
                res = fetcher.retrieve_article_info(article['url'])
                print(res['success'])
                article_contents = res['plain_text'] if res['success'] else None
                filled.append({
                    'title': article['title'],
                    'passage': article_contents
                })
    result = summarizer.summarize(filled, query=None)
    print("[{}] TOTAL ELAPSED END".format(time.time()-t00), file=sys.stderr)
    print("RESULT ", result)
    result['error'] = False
    return jsonify(result)

@app.route('/api/v1.0/newsfeed/get_query_summary', methods=['GET'])
def get_query_summary():
    query = request.args.get('query')

    t00 = time.time()
    t0 = time.time()
    print("[{}] starting ".format(time.time()-t0), file=sys.stderr); t0 = time.time();
    summarizer = Summarizer()
    filled = []
    print("[{}] before simple_fetch ".format(time.time()-t0), file=sys.stderr)
    articles = fetcher.simple_fetch()
    print("[{}] did simple_fetch ".format(time.time()-t0), file=sys.stderr)
    #for a in articles:
    for idx, a in enumerate(articles):  # TODO: can we check through all the articles quickly?
        res = fetcher.retrieve_article_info(a['url'])
        article_contents = res['plain_text'] if res['success'] else None
        filled.append({
            'title': a['title'],
            'passage': article_contents
        })
        print("[{}] article {} done".format(time.time()-t0,idx), file=sys.stderr); t0 = time.time()
    result = summarizer.summarize(filled, query=query)
    print("[{}] TOTAL ELAPSED END".format(time.time()-t00), file=sys.stderr)
    return jsonify(result)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0',port=8888,debug=True)
    except Exception as e:
        print('exception: ', e)
        tb = traceback.format_exc()
        print(tb)
        raise e
