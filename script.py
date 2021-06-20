import re
import os
import os.path
import json
import codecs
from datetime import date, datetime
from instalooter.looters import ProfileLooter
from instalooter.looters import HashtagLooter
import flask
from flask_cors import CORS
from flask import request, json

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

@app.route('/', methods=['GET'])
def home():
    iter = 0
    results = []

    max_results = 12
    if 'max_results' in request.args:
        max_results = int(request.args['max_results'])

    hashtag = "quoteslucu"
    if 'hashtag' in request.args:
        hashtag = request.args['hashtag']

    looter = HashtagLooter(hashtag)
    looter.download('.', media_count=max_results)
    today = date.today()
    filename = hashtag + str(today) + ".txt"

    def links(media, looter):
        if media.get('__typename') == "GraphSidecar":
            media = looter.get_post_info(media['shortcode'])
            nodes = [e['node'] for e in media['edge_sidecar_to_children']['edges']]
            return [n.get('video_url') or n.get('display_url') for n in nodes]
        media = looter.get_post_info(media['shortcode'])
        text = media['edge_media_to_caption']['edges'][0]['node']['text']
        return [{'image': media['display_url'], 'caption': text, 'username': media['owner']['username'], 'shortcode': media['shortcode'], 'id': media['id']}]

    if not os.path.isfile('./' + filename):
        with codecs.open(filename, "w", "utf-8") as f:
                for media in looter.medias():
                    if iter < max_results:
                        iter += 1
                        for detail in links(media, looter):
                            results.append(detail)
                    else:
                        json_str = json.dumps(results, indent=2)
                        f.write(json_str)
                        break
        f.close()

    f = open(filename, "r")
    json_str = f.read()
    response = app.response_class(
        response=json_str,
        status=200,
        mimetype='application/json'
    )
    return response

app.run(host='0.0.0.0', port=5780)