from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__,instance_relative_config=True)

app.wsgi_app = ProxyFix(app.wsgi_app)

app.config.from_object('config')
app.config.from_pyfile('config.py')

from . import views
