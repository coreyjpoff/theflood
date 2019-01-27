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

# Constants
# CLIENT_ID = json.loads(
#     open('client_secrets.json', 'r').read()
# )['web']['client_id']
# column User.role
USER_ROLE = 'USER'
EDITOR_ROLE = 'EDITOR'
ADMIN_ROLE = 'ADMIN'
# column ArticleResource.resource_type
TITLE_IMAGE = 'TITLE_IMAGE'
IMAGE = 'IMAGE'
FOOTNOTE = 'FOOTNOTE'

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

@app.route('/login')
def showLogin():
    # TODO: See if i'm already logged in?
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# XCJP Come back here when implemented--didn't switch DBs
@app.route('/login/<provider>', methods=['POST'])
def login(provider):
    # Validate state token
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    auth_code = request.data
    if provider == 'google':
        return googleLogin(auth_code)
    else:
        response = make_response(
            json.dumps('Unrecognized Provider'),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

# XCJP Come back here when implemented--didn't switch DBs
@app.route('/logout')
def logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected'), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    if login_session.get('provider') == 'google':
        return googleLogout(access_token)
    else:
        response = make_response(
            json.dumps('Unrecognized Provider'), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

# XCJP check login
@app.route('/edit/')
def showEditorHome():
    # if not isEditorOrAdmin(login_session.get('role')):
    #     return redirect(url_for('showHome'))
    articles = getAllArticles(False, True)
    authors = {}
    images = {}
    for article in articles:
        authors[article[0]] = getAuthorsForArticle(article[0])
        images[article[0]] = getTitleImageForArticle(article[0])
    return render_template(
        'edit.html',
        articles=articles,
        authors=authors,
        images=images,
    )

# XCJP implement or delete
# @app.route('/edit/admin')
def showAdminInfo():
    # if not isAdmin(login_session.get('role')):
    #     return redirect(url_for('showHome'))
    return render_template('editAdmin.html')

# XCJP check login
@app.route('/edit/<string:editor>/<int:article_id>', methods=['GET', 'POST'])
def editArticle(article_id,editor):
    article = getArticle(article_id, True)
    authors = getAuthorsForArticle(article_id)
    allAuthors = getAllAuthors()
    image = getTitleImageForArticle(article_id)
    other_files = getNontitleImagesForArticle(article_id)
    # if not isEditorOrAdmin(login_session.get('role')):
    #     return redirect(url_for('showHome'))
    if request.method == 'POST':
        error = saveExistingArticleFromForm(article, request.form)
        error = saveAuthorsForArticleFromForm(article[0], request.form)
        if request.form.get('is_hidden') and request.form['is_hidden']:
            return redirect(url_for('showEditorHome'))
        else:
            return redirect(url_for(
                'showArticle',
                article_id=article[0],
                url_desc=article[5],
            ))
    elif editor == 'raw':
        isRawText = True
    else:
        isRawText = False
    return render_template(
        'editArticle.html',
        article=article,
        authors=authors,
        allAuthors=allAuthors,
        image=image,
        other_files=other_files,
        isRawText = isRawText
    )

# XCJP check login
# @app.route('/edit/new', methods=['GET', 'POST'])
def newArticle():
    article = [-1,'','',None,None,'','',True,False,0,'',False]
    authors = []
    allAuthors = getAllAuthors()
    image = []
    other_files = []
    # TODO: handle the authors, pics, etc whatever i do in edit--can i combine these?
    # if not isEditorOrAdmin(login_session.get('role')):
    #     return redirect(url_for('showHome'))
    if request.method == 'POST':
        data = saveNewArticleFromForm(article, request.form)
        error = saveAuthorsForArticleFromForm(data[0], request.form)
        return redirect(url_for(
            'showArticle',
            article_id=data[0],
            url_desc=data[5],
            articleToShow=data
        ))
    else:
        return render_template(
            'editArticle.html',
            article=article,
            authors=authors,
            allAuthors=allAuthors,
            image=image,
            other_files=other_files
        )

# @app.route('/edit/authors/')
def editAuthorsHome():
    authors = getAllAuthors()
    return render_template('editAuthors.html', authors=authors)

# @app.route('/edit/authors/<int:auth_id>/', methods=['GET', 'POST'])
def editAuthor(auth_id):
    author = getAuthor(auth_id)
    if request.method == 'POST':
        saveExistingAuthorFromForm(author, request.form)
        return redirect(url_for('editAuthorsHome'))
    else:
        return render_template('editAuthor.html', author=author)

# @app.route('/edit/authors/new/', methods=['GET', 'POST'])
def newAuthor():
    author = [-1, None, None]
    if request.method == 'POST':
        author = saveNewAuthorFromForm(author, request.form)
        return redirect(url_for('editAuthorsHome'))
    else:
        return render_template('editAuthor.html', author=author)

# XCJP Come back here when implemented--didn't switch DBs
# @app.route('/edit/home')
def editHomePage():
    if not isEditorOrAdmin(login_session.get('role')):
        return redirect(url_for('showHome'))
    return render_template('editHome.html')

# @app.route('/email-list')
def showEmailList():
    # XCJP add security/login check
    try:
        sql = """SELECT * FROM subscriber; """
        cur.execute(sql)
        emailList = cur.fetchall()
        return render_template('showEmailList.html', emailList=emailList)
    except(Exception, psycopg2.DatabaseError) as error:
        return error

# XCJP check login
# @app.route('/edit/upload/<int:article_id>/<string:type>', methods=['GET', 'POST'])
def uploadFiles(article_id, type):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('File not sent')
            return redirect(url_for('showEditorHome'))
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('showEditorHome'))
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER'] + str(article_id) + '/'
            # XCJP consider updating to all relative paths
            if type == 'audio':
                filepath = filepath + 'audio/'
                relativePath = RELATIVE_UPLOAD_PATH + str(article_id) + '/audio/'
            else:
                relativePath = RELATIVE_UPLOAD_PATH + str(article_id) + '/'
            if not os.path.isdir(filepath):
                os.makedirs(filepath)
            file.save(os.path.join(filepath, filename))
            article = getArticle(article_id, True)
            saveArticleResourceFromForm(article_id, request.form, filename, relativePath, type)
            return redirect(url_for('editArticle', article_id=article_id, editor='editor'))
        else:
            return render_template('uploadFiles.html', article_id=article_id, type=type)
    else:
        return render_template('uploadFiles.html', article_id=article_id, type=type)
        # XCJP here for deleting resource
        # article_resources = getAllResourcesForArticle(article_id)
        #     article_resources = article_resources
        # )

# XCJP update this to avoid using get method
# @app.route('/edit/delete/resource/<int:id>/<int:article_id>')
def deleteResource(id, article_id):
    try:
        sql = """SELECT resource_location FROM article_resource WHERE id=%s;"""
        cur.execute(sql, (str(id),))
        path = cur.fetchone()[0]
        sql = """DELETE FROM article_resource WHERE id=%s; """
        cur.execute(sql, (str(id),))
        conn.commit()
        os.remove(str(path))
        return redirect(url_for('editArticle', article_id=article_id, editor='editor'))
    except (Exception, psycopg2.DatabaseError) as error:
        return error

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

def parseTextElements(article_text, image_list):
    # article_text = re.split(r'\{\{(img|break|foot)?(: ([0-9]+|[a-zA-Z]+)\}\}')
    article_text = re.sub(
        r'\{\{break\}\}', '',
        article_text
    )
    # '<img class="page-break", alt="Page break", src="/static/page-break.png">',
    return article_text

# XCJP update
def googleLogin(auth_code):
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json',
            scope=''
        )
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code'),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match user ID"),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app client ID"),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # See if user is already connected
    stored_access_token = login_session.get('access_token')
    stored_g_id = login_session.get('g_id')
    if stored_access_token is not None and g_id == stored_g_id:
        response = make_response(
            json.dumps('Current user is already connected'),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in session
    login_session['access_token'] = credentials.access_token
    login_session['g_id'] = g_id
    # Get user info and store in session
    url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    result = requests.get(url, params=params)
    data = result.json()
    if data['name']:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']
    login_session['signin_email'] = data['email']
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id, role = getUserIDandRole(data["email"])
    if not user_id:
        user_id, role = createUser(login_session)
    login_session['user_id'] = user_id
    login_session['role'] = role

    return login_session['username']


def googleLogout(access_token):
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['g_id']
        del login_session['username']
        del login_session['signin_email']
        del login_session['provider']
        del login_session['user_id']
        del login_session['role']
        return redirect(url_for('showHome'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user'),
            400
        )
        response.headers['Content-Type'] = 'applicatin/json'
        return response

# XCJP update
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        signin_email=login_session['signin_email'],
        active_email=login_session['signin_email'],
        role=USER_ROLE
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(signin_email=login_session['signin_email']).one()
    return user.id, user.role

# XCJP update
def getUserIDandRole(email):
    try:
        user = session.query(User).filter_by(signin_email=email).one()
        return user.id, user.role
    except:
        return None, None


def isEditorOrAdmin(role):
    if isAdmin(role):
        return True
    if role == EDITOR_ROLE:
        return True
    return False


def isAdmin(role):
    if role == ADMIN_ROLE:
        return True
    return False


if __name__ == '__main__':
    # app.run()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
