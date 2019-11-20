from flask import Flask

from eventbot import settings

app = Flask(__name__)
app.config.from_object(settings)
