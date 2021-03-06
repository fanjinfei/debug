# from http://flask.pocoo.org/ tutorial
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import render_template, redirect, g, url_for, abort
from flask import send_from_directory
from flask.ext.babel import Babel
from flask_paginate import Pagination, get_page_parameter
import requests
import json
import sys

import pprint

templates_dir = sys.argv[1]
static_dir = sys.argv[2]
base_url = 'http://dev-b-es-fusion01.stc.ca:8080/json/?'
app = Flask(__name__, template_folder=templates_dir)
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './i18n'
babel = Babel(app)
CORS(app)
'''
pybabel init -i fr.po -d ./i18n/ -l fr
pybabel compile -d i18n/
later only 	$ pybabel update -i fr.po -d i18n
'''

@app.before_request
def before():
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] not in ('fr', 'en'):
            return abort(404)
        g.current_lang = request.view_args['lang_code']
        request.view_args.pop('lang_code')

@babel.localeselector
def get_locale():
    return g.get('current_lang', 'en')

@app.route('/')
def root():
    return redirect(url_for('search', lang_code='en'))

def _send_static(filename):
    return send_from_directory(static_dir, filename)

#@app.route('/<string:page_name>/')
@app.route('/static/<string:page_name>')
def static_page(page_name):
    return _send_static(page_name)
    #return render_template('%s' % page_name)

@app.route('/css/<string:page_name>')
def css_page(page_name):
    return _send_static(page_name)

def _get_search(q, start_page=1, page_size=20, label=None, burl=None):
    start = (start_page-1)*page_size
    if not burl: burl=base_url
    if label:
        q = q + '+label%3A' +label
    url = ''.join([burl, 'q=', q, '&start={0}&num={1}'.format(start,page_size)])
    print (url)
    user_agent = {'User-agent': 'statcan search'}
    r = requests.get(url=url, headers=user_agent, timeout=10)
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        return None

@app.route("/suggest", methods=['GET'])
def suggest():
    qval = request.args.get('query')
    callback = request.args.get('callback')
    url = 'http://dev-b-es-fusion01.stc.ca:8080/suggest?callback={1}&query={0}&fields=_default,content,title&num=20'.format(qval, callback)
    r = requests.get(url=url, timeout=2)
    if r.status_code == requests.codes.ok:
        return r.text
        r= json.loads(r.text[11:-1])['response']['result']['hits']
        r = [p['text'] for p in r]
        return json.dumps(r)

@app.route("/<lang_code>/search", methods=['GET'])
def search():
    qval = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    print (qval, request.get_json(), request.data, request.args)
    res = None
    pagination = None
    if qval:
        res = _get_search(qval, page)
        if res:
            res = json.loads(res)['response']
            total, per_page = res['record_count'], 20
            href=''.join(['/en/search?q=',qval,
                           '&num=20&page={0}'])
            if total > per_page:
                pagination = Pagination(page=page, per_page=per_page,
                                    href = href, bs_version=4,
                                    total=total, record_name='users')
    return render_template('index.html', qval=qval or '', res=res, locale=get_locale(),
                           pagination=pagination)

@app.route("/<lang_code>/ib_search", methods=['GET'])
def ib_search():
    qval = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    print (qval, request.get_json(), request.data, request.args)
    res = None
    pagination = None
    if qval:
        res = _get_search(qval, page, 20, 'ib', 'http://f7wcmstestb2.statcan.ca:9601/json/?')
        if res:
            res = json.loads(res)['response']
            total, per_page = res['record_count'], 20
            href=''.join(['/en/search?q=',qval,
                           '&num=20&page={0}'])
            if total > per_page:
                pagination = Pagination(page=page, per_page=per_page,
                                    href = href, bs_version=4,
                                    total=total, record_name='users')
    return render_template('index_ib.html', qval=qval or '', res=res, locale=get_locale(),
                           pagination=pagination)

@app.route("/<lang_code>/ecn_search", methods=['GET'])
def ecn_search():
    qval = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    print (qval, request.get_json(), request.data, request.args)
    res = None
    pagination = None
    if qval:
        res = _get_search(qval, page, 20, 'ecn', 'http://f7wcmstestb2.statcan.ca:9601/json/?')
        if res:
            res = json.loads(res)['response']
            total, per_page = res['record_count'], 20
            href=''.join(['/en/search?q=',qval,
                           '&num=20&page={0}'])
            if total > per_page:
                pagination = Pagination(page=page, per_page=per_page,
                                    href = href, bs_version=4,
                                    total=total, record_name='users')
    return render_template('index.html', qval=qval or '', res=res, locale=get_locale(),
                           pagination=pagination)


@app.route("/<lang_code>/adv_search", methods=['GET'])
def advanced_search():
    qval=None
    res=None
    return render_template('adv.html', qval=qval or '', res=res, locale=get_locale(),
                           pagination=None)

@app.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.ico')

def test():
    r = json.loads(_get_search('price'))
    pprint.pprint(r)

@app.route('/api/data')
def api_data():
    data = {}
    return jsonify(data)


if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8000)
    #test()

    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('', 8001), app)
    http_server.serve_forever()

