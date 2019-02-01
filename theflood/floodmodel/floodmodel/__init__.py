#!/usr/bin/env python2.7

from flask import Flask
app = Flask(__name__)

import floodmodel.sqlquery
import floodmodel.author
import floodmodel.resource
import floodmodel.subscriber
import floodmodel.article
