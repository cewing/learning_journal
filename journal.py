# -*- coding: utf-8 -*-
from flask import Flask


DB_SCHEMA = """
DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""


app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True)
