#coding=utf-8
from flask import Flask
from core.analytics import analytics

app = Flask(__name__)
app.register_blueprint(analytics)

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)