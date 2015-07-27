from . import app
from . import models

@app.route('/')
def home():
    return "Hello!"
