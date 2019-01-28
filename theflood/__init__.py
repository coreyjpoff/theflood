#!/usr/bin/env python2.7

import sys
from flask import Flask

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
import theflood.views
