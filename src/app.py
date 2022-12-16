import json
import logging
import os
import json
import urllib.parse
import requests

import furl
from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
from paste.translogger import TransLogger

# Searcher for Fedora2 / AdminTools

# Add any environment variables from .env
load_dotenv('../.env')

# Get environment variables
env = {}
for key in ('FEDORA2_SOLR_URL', 'FEDORA2_SOLR_FILTER_QUERY', 
            'FEDORA2_LINK', 'FEDORA2_NO_RESULTS_LINK', 'FEDORA2_MODULE_LINK'):
    env[key] = os.environ.get(key)
    if env[key] is None:
        raise RuntimeError(f'Must provide environment variable: {key}')

solr_url = furl.furl(env['FEDORA2_SOLR_URL'])
search_url = solr_url / 'select'
search_fq = env['FEDORA2_SOLR_FILTER_QUERY']
link = env['FEDORA2_LINK']
no_results_link = env['FEDORA2_NO_RESULTS_LINK']
module_link = env['FEDORA2_MODULE_LINK']

debug = os.environ.get('FLASK_DEBUG')

logging.root.addHandler(logging.StreamHandler())

loggerWaitress = logging.getLogger('waitress')
logger = logging.getLogger('fedora2-searcher')

if debug:
    loggerWaitress.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

else:
    loggerWaitress.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

logger.info("Starting the fedora2-searcher Flask application")

endpoint = 'fedora2-search'


# Start the flask app, with compression enabled
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/ping')
def ping():
    return {'status': 'ok'}


@app.route('/search')
def search():

    # Get the request parameters
    args = request.args
    if 'q' not in args or args['q'] == "":
        return {
            'endpoint': endpoint,
            'error': {
                'msg': 'q parameter is required',
            },
        }, 400
    query = args['q']

    per_page = 3
    if 'per_page' in args and args['per_page'] != "":
        per_page = args['per_page']

    page = 0
    if 'page' in args and args['page'] != "" and args['page'] != "%":
        page = args['page']

    start = int(page) * int(per_page)
    rows = per_page

    # Execute the search
    params = {
        'q': query,
        'df': 'dmKeyword',
        'rows': rows,  # number of results
        'start': start,  # starting at this result (0 is the first result)
        'fq': search_fq, # filter query
        'wt': 'json', # get JSON format results
        'sort': 'score desc',
        'fl': 'displayTitle,itemType,dmDate,collectionTitle,pid,hensonDescription,thumbnail110',
        'version': '2',
        'hl': 'true',
        'hl.fragsize': '500',
        'hl.simple.pre': '<b>',
        'hl.simple.post': '</b>',
        'hl.fl': 'displayTitle',
    }
    try:
        response = requests.get(search_url.url, params=params)
    except Exception as err:
        logger.error(f'Error submitting search url={search_url.url}, params={params}\n{err}')

        return {
            'endpoint': endpoint,
            'error': {
                'msg': f'Error submitting search',
            },
        }, 500

    if response.status_code != 200:
        logger.error(f'Received {response.status_code} when submitted {query=}')

        return {
            'endpoint': endpoint,
            'error': {
                'msg': f'Received {response.status_code} when submitted {query=}',
            },
        }, 500

    logger.debug(f'Submitted url={search_url.url}, params={params}')
    logger.debug(f'Received response {response.status_code}')
    logger.debug(response.text)

    data = json.loads(response.text)

    # Gather the search results into our response
    results = []
    response = {
        'endpoint': endpoint,
        'query': query,
        "per_page": str(per_page),
        "page": str(page),
        "total": int(data['response']['numFound']),
        "module_link": module_link.replace('{query}',
                                           urllib.parse.quote_plus(query)),
        "no_results_link": no_results_link,
        "results": results
    }

    if 'docs' in data['response']:
        for item in data['response']['docs']:

            id = item['pid']

            highlight = ''
            if 'displayTitle' in data['highlighting'][id]:
                highlight = data['highlighting'][id]['displayTitle']

            results.append({
                'title': item['displayTitle'],
                'link': link.replace('{id}',
                        urllib.parse.quote_plus(id)),
                'description': item['hensonDescription'] if 'hensonDescription' in item else '',
                'item_format': item['itemType'],
                'extra': {
                    'collection': item['collectionTitle'][0] if 'collectionTitle' in item  else '',
                    'htmlSnippet': highlight,
                    'thumbnail': item['thumbnail110'] if 'thumbnail110' in item else '',
                },
            })

    return response


if __name__ == '__main__':
    # This code is not reached when running "flask run". However the Docker
    # container runs "python app.py" and host='0.0.0.0' is set to ensure
    # that flask listens on port 5000 on all interfaces.

    # Run waitress WSGI server
    serve(TransLogger(app, setup_console_handler=True),
          host='0.0.0.0', port=5000, threads=10)
