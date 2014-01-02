# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from app import create_app

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0')
