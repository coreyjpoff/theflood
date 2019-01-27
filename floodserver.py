#!/usr/bin/env python2.7

import sys
import os
import random
import string
import httplib2
import json
import requests
import re
from flask import Flask, render_template, request, redirect, url_for, \
    make_response, jsonify, g
from flask import session as login_session
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import psycopg2
from werkzeug.utils import secure_filename
from article import Article

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
UPLOAD_FOLDER = '/home/flood/theflood/static/articles/'
RELATIVE_UPLOAD_PATH = '/static/articles/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

conn = psycopg2.connect(database="flood", user="flood", password="flood")
cur = conn.cursor()

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
        errorText = saveSubscriberFromForm(request.form)
        if not errorText:
            return redirect(url_for('showHome'))
        else:
            return render_template('subscribe.html', error=errorText)
    else:
        return render_template('subscribe.html', error='')

# helper functions
def getAllArticles(on_home=False, include_hidden=False):
    try:
        if not include_hidden:
            if on_home:
                sql = """SELECT * FROM article
                    WHERE on_home = 't' AND is_hidden = 'f'
                    ORDER BY priority DESC, id ASC; """
            else:
                sql = """SELECT * FROM article
                    WHERE is_hidden = 'f'
                    ORDER BY priority DESC, id ASC; """
        else:
            if on_home:
                sql = """SELECT * FROM article
                    WHERE on_home = 't'
                    ORDER BY priority DESC, id ASC; """
            else:
                sql = """SELECT * FROM article
                    ORDER BY priority DESC, id ASC; """
        cur.execute(sql)
        articles = cur.fetchall()
        return articles
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def getArticle(article_id, allow_hidden):
    try:
        if allow_hidden:
            sql = """
                SELECT * FROM article a
                WHERE a.id = %s; """ % str(article_id)
        else:
            sql = """
                SELECT * FROM article a
                WHERE a.id = %s AND a.is_hidden = 'f'; """ % str(article_id)
        cur.execute(sql)
        article = cur.fetchone()
        return article
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def saveExistingArticleFromForm(article, form):
    article = getArticleDataFromForm(article, form)
    try:
        sql = """UPDATE article SET (title,subtitle,issue,url_desc,html_text,on_home,featured,priority,lead,is_hidden)
            =(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            WHERE id=%s; """
        data = (article[1], article[2], article[4], article[5], article[6], article[7], article[8], article[9], article[10], article[11], article[0])
        cur.execute(sql, data)
        conn.commit()
        return ''
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def saveNewArticleFromForm(article, form):
    article = getArticleDataFromForm(article, form)
    try:
        sql = """INSERT INTO article (title,subtitle,issue,url_desc,html_text,on_home,featured,priority,lead,is_hidden)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;"""
        data = (article[1], article[2], article[4], article[5], article[6], article[7], article[8], article[9], article[10],article[11])
        cur.execute(sql, data)
        conn.commit()
        savedData = cur.fetchone()
        return savedData
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def getArticleDataFromForm(article, form):
    if form.get('title'):
        title = form['title']
    else:
        title = ''
    if form.get('subtitle'):
        subtitle = form['subtitle']
    else:
        subtitle = ''
    if article[5]:
        url_desc = article[5]
    else:
        urlDescLen = min(len(title), 5)
        url_desc = ''.join(c for c in title if (
            c.isalnum() or c == ' '
        ))
        url_desc = '-'.join(url_desc.split()[:urlDescLen]).lower()
    if form.get('html_text'):
        html_text = form['html_text']
    else:
        html_text = ''
    if form.get('issue'):
        issue = form['issue']
    else:
        issue = 0
    if form.get('priority'):
        priority = form.get('priority')
    else:
        priority = 0
    if form.get('lead'):
        lead = form.get('lead')
    else:
        lead = ''
    if form.get('on_home'):
        on_home = form['on_home']
    else:
        on_home = False
    if form.get('featured'):
        featured = form['featured']
    else:
        featured = False
    if form.get('is_hidden'):
        is_hidden = form['is_hidden']
    else:
        is_hidden = False
    return [article[0], title, subtitle, article[3], issue, url_desc,
        html_text, on_home, featured, priority, lead, is_hidden]

def saveAuthorsForArticleFromForm(article_id, form):
    newAuthorsIds = form.getlist('authors')
    deleted = deleteAllOldAuthorsForArticle(article_id)
    if newAuthorsIds and newAuthorsIds[0] == '-1':
        return ''
    newAuthor = None
    error = ''
    for newAuthorId in newAuthorsIds:
        error = saveNewAuthorForArticle(article_id, newAuthorId)
    return error

def deleteAllOldAuthorsForArticle(article_id):
    try:
        sql = """DELETE FROM article_author
            WHERE article_id=%s; """
        cur.execute(sql, (str(article_id),))
        conn.commit()
        return ''
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def saveNewAuthorForArticle(article_id, author_id):
    try:
        sql = """INSERT INTO article_author (article_id, author_id)
            VALUES (%s, %s); """
        cur.execute(sql, (str(article_id), str(author_id)))
        conn.commit()
        return ''
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def saveNewAuthorFromForm(author, form):
    author = getAuthorDataFromForm(author, form)
    try:
        sql = """INSERT INTO author (name, bio)
            VALUES (%s, %s) RETURNING *;"""
        data = (author[1], author[2])
        cur.execute(sql, data)
        savedData = cur.fetchone()
        conn.commit()
        return savedData
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def getAuthorDataFromForm(author, form):
    if form.get('name'):
        name = form['name']
    else:
        name = ''
    if form.get('bio'):
        bio = form['bio']
    else:
        bio = ''
    return [author[0], name, bio]

def saveExistingAuthorFromForm(author, form):
    author = getAuthorDataFromForm(author, form)
    try:
        sql = """UPDATE author SET (name, bio)
            =(%s, %s) WHERE id = %s;"""
        data = (author[1], author[2], author[0])
        cur.execute(sql, data)
        savedData = cur.fetchone()
        conn.commit()
        return savedData
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def saveArticleResourceFromForm(article_id, form, filename, filepath, resource_type):
    resource = getResourceData(article_id, form)
    try:
        sql = """INSERT INTO article_resource (name,article_id,resource_type,is_title_img,caption,resource_location)
            VALUES (%s, %s, %s, %s, %s, %s);"""
        data = (filename, article_id, resource_type, resource[0], resource[1], filepath + filename)
        cur.execute(sql, data)
        conn.commit()
        return ''
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def getResourceData(article_id, form):
    if form.get('is_title_img'):
        is_title_img = form['is_title_img']
    else:
        is_title_img = False
    if form.get('caption'):
        caption = form['caption']
    else:
         caption = ''
    return [is_title_img, caption]

def getAllResourcesForArticle(article_id):
    try:
        sql = """
        SELECT * FROM author
        WHERE article_id = %s; """ % str(article_id)
        cur.execute(sql)
        article_resources = cur.fetchall()
        return article_resources
    except(Exception, psycopg2.DatabaseError) as error:
        return error

# XCJP add some email verification
def saveSubscriberFromForm(form):
    if not form.get('name'):
        return "Name is required"
    if not form.get('email'):
        return "Email is required"
    if findSubscriber(form.get('email')):
        return "That email address is already subscribed"
    try:
        sql = """INSERT INTO subscriber (email_address,name)
            VALUES (%s, %s); """
        data = (form.get('email'), form.get('name'))
        cur.execute(sql, data)
        conn.commit()
        return ''
    except (Exception, psycopg2.DatabaseError) as error:
        return error

def findSubscriber(email):
    try:
        sql = """SELECT * FROM subscriber s
            WHERE s.email_address = '%s'; """ % email
        cur.execute(sql)
        return cur.fetchone()
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def getAuthorsForArticle(article_id):
    try:
        sql = """
        SELECT a.id, a.name, a.bio FROM author a
            JOIN article_author aa
            ON a.id = aa.author_id
            WHERE aa.article_id = %s; """ % str(article_id)
        cur.execute(sql)
        authors = cur.fetchall()
        return authors
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def getAllAuthors():
    try:
        sql = """SELECT * FROM author; """
        cur.execute(sql)
        authors = cur.fetchall()
        return authors
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def getAuthor(auth_id):
    try:
        sql = """SELECT * FROM author
        WHERE id = %s; """ % str(auth_id)
        cur.execute(sql)
        author = cur.fetchone()
        return author
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def getTitleImageForArticle(article_id):
    try:
        sql = """
            SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 't'; """ % str(article_id)
        cur.execute(sql)
        image = cur.fetchone()
        return image
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def getNontitleImagesForArticle(article_id):
    try:
        sql = """
            SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 'f'; """ % str(article_id)
        cur.execute(sql)
        images = cur.fetchall()
        return images
    except(Exception, psycopg2.DatabaseError) as error:
        return error

def allowedFile(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
