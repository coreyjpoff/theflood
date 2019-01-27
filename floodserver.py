#!/usr/bin/env python2.7

import sys
import os
import string
import re
from flask import Flask, render_template, request, redirect, url_for
from article import Article
from subscriber import Subscriber

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)

# page renders
@app.route('/home/')
@app.route('/')
def showHome():
    articles = Article.getHomePageArticles()
    return render_template(
        'home.html',
        articles=articles,
    )

@app.route('/archive/')
def showArchive():
    articles = Article.getArchiveArticles()
    return render_template(
        'archive.html',
        articles=articles,
    )

@app.route('/archive/<string:url_desc>/<int:article_id>')
def showArticle(article_id, url_desc, articleToShow=None):
    if articleToShow is None:
        article = Article.fromID(article_id)
    if article is None:
        return redirect(url_for('showHome'))
    return render_template(
        'article.html',
        article=article,
    )

@app.route('/about')
def showAbout():
    return render_template('about.html')

@app.route('/contact')
def showContact():
    return render_template('contact.html')

@app.route('/submissions')
def showSubmissions():
    return render_template('submissions.html')

@app.route('/subscribe', methods=['GET', 'POST'])
def showSubscribe():
    if request.method == 'POST':
        errorText = Subscriber.saveSubscriberFromForm(request.form)
        if errorText is None:
            return redirect(url_for('showHome'))
        else:
            return render_template('subscribe.html', error=errorText)
    else:
        return render_template('subscribe.html', error='')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
