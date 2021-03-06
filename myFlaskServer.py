# from http://flask.pocoo.org/ tutorial
from flask import Flask
from flask import render_template
app = Flask(__name__, template_folder="/home/jffan/src/debug/")

from flask import send_from_directory

@app.route('/<string:page_name>/')
def static_page(page_name):
    return render_template('%s' % page_name)
    #return "Hello World! [" + page_name + "]"
    #return render_template('%s.html' % page_name)


@app.route("/") # take note of this decorator syntax, it's a common pattern
def hello():
    return "Hello World!"

@app.route("/app") # take note of this decorator syntax, it's a common pattern
def app1():
    return "Hello app World!"

@app.route("/photo") # take note of this decorator syntax, it's a common pattern
def photo():
    return "Hello photo World!"

@app.route('/favicon.ico')
def favicon():
    print ('hi fav')
    return send_from_directory('/home/jffan/src/debug/static/',
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
