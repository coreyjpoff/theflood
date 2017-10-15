#!/usr/bin/env python3
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
from database_setup import Base, User, Article, Author, ArticleAuthor, \
    ArticleResource, Subscriber
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

engine = create_engine('sqlite:///flood.db')
Base.metadata.bind = engine
BDSession = sessionmaker(bind=engine)
session = BDSession()

# Constants
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read()
)['web']['client_id']
# column User.role
USER_ROLE = 'USER'
EDITOR_ROLE = 'EDITOR'
ADMIN_ROLE = 'ADMIN'
# column ArticleResource.resource_type
TITLE_IMAGE = 'TITLE_IMAGE'
IMAGE = 'IMAGE'
FOOTNOTE = 'FOOTNOTE'


# JSON APIs TODO: come back and clean these up so they're useful
@app.route('/archive/JSON')
def showArchiveJSON():
    articles = session.query(Article).all()
    return jsonify(Articles=[a.serialize for a in articles])


@app.route('/archive/<int:article_id>/JSON')
def showArticleJSON(article_id):
    article = getArticle(article_id)
    return jsonify(Articles=[article.serialize])


@app.route('/archive/<int:article_id>/authors/JSON')
def showArticleAuthorsJSON(article_id):
    authors = getAuthorsForArticle(article_id)
    return jsonify(Authors=[a.serialize for a in authors])


@app.route('/archive/authors/JSON')
def showAuthorsJSON():
    authors = session.query(Author).all()
    return jsonify(Authors=[a.serialize for a in authors])


@app.route('/archive/authors/<int:author_id>/JSON')
def showAuthorArticlesJSON(author_id):
    articles = getArticlesForAuthor(author_id)
    return jsonify(Articles=[a.serialize for a in articles])


# page renders
@app.route('/home/')
@app.route('/')
def showHome():
    articles = session.query(Article).filter_by(on_home=True).order_by(desc(Article.priority)).all()
    authors = {}
    images = {}
    for article in articles:
        print(article.lead)
        authors[article.id] = getAuthorsForArticle(article.id)
        images[article.id] = getTitleImageForArticle(article.id)
    return render_template(
        'home.html',
        articles=articles,
        authors=authors,
        images=images
    )


@app.route('/archive/')
def showArchive():
    articles = session.query(Article).order_by(desc(Article.publish_date), desc(Article.priority)).all()
    authors = {}
    images = {}
    for article in articles:
        authors[article.id] = getAuthorsForArticle(article.id)
        images[article.id] = getTitleImageForArticle(article.id)
    return render_template(
        'archive.html',
        articles=articles,
        authors=authors,
        images=images
    )


@app.route('/archive/<string:url_desc>/<int:article_id>')
def showArticle(article_id, url_desc):
    articleToShow = getArticle(article_id)
    image = getTitleImageForArticle(articleToShow.id)
    other_images = getNontitleImagesForArticle(articleToShow.id)
    authors = getAuthorsForArticle(articleToShow.id)
    # articleToShow.html_text = parseTextElements(
    #     articleToShow.html_text,
    #     other_images
    # )
    # TODO: finish this or take it out
    return render_template(
        'article.html',
        article=articleToShow,
        authors=authors,
        image=image,
        other_images=other_images
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

# TODO: add a post method
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


@app.route('/edit/')
def showEditorHome():
    if not isEditorOrAdmin(login_session.get('role')):
        return redirect(url_for('showHome'))
    articles = session.query(Article).all()
    return render_template('edit.html', articles=articles)


@app.route('/edit/admin')
def showAdminInfo():
    if not isAdmin(login_session.get('role')):
        return redirect(url_for('showHome'))
    return render_template('editAdmin.html')


@app.route('/edit/<int:article_id>', methods=['GET', 'POST'])
def editArticle(article_id):
    article = getArticle(article_id)
    authors = getAuthorsForArticle(article_id)
    if not isEditorOrAdmin(login_session.get('role')):
        return redirect(url_for('showHome'))
    if request.method == 'POST':
        saveArticleFromForm(article, request.form)
        return redirect(url_for(
            'showArticle',
            article_id=article.id,
            url_desc=article.url_desc,
            authors=authors
        ))
    else:
        return render_template(
            'editArticle.html',
            article=article,
            authors=authors
        )


@app.route('/edit/new', methods=['GET', 'POST'])
def newArticle():
    article = Article()
    # TODO: handle the authors, pics, etc whatever i do in edit--can i combine these?
    if not isEditorOrAdmin(login_session.get('role')):
        return redirect(url_for('showHome'))
    if request.method == 'POST':
        saveArticleFromForm(article, request.form)
        return redirect(url_for(
            'showArticle',
            article_id=article.id,
            url_desc=article.url_desc
        ))
    else:
        return render_template('editArticle.html', article=article)


@app.route('/edit/home')
def editHomePage():
    if not isEditorOrAdmin(login_session.get('role')):
        return redirect(url_for('showHome'))
    return render_template('editHome.html')


# helper functions
def getArticle(article_id):
    try:
        article = session.query(Article).filter_by(id=article_id).one()
        if article.html_text:
            article.html_text = article.html_text.replace("{{pull:", "}}test:")
        return article
    except:
        return None
    
    
def saveArticleFromForm(article, form):
    if form.get('title'):
        article.title = form['title']
    if form.get('subtitle'):
        article.subtitle = form['subtitle']
    urlDescLen = min(len(article.title), 5)
    article.url_desc = ''.join(c for c in article.title if (
        c.isalnum() or c == ' '
    ))
    article.url_desc = '-'.join(article.url_desc.split()[:urlDescLen]).lower()
    if form.get('html_text'):
        article.html_text = form['html_text']
    article.on_home = form.get('on_home')
    article.featured = form.get('featured')
    session.add(article)
    session.commit()


def saveSubscriberFromForm(form):
    if not form.get('name'):
        return "Name is required"
    if not form.get('email'):
        return "Email is required"
    if len(session.query(Subscriber).filter_by(email_address=form.get('email')).all()) > 0:
        return "That email address is already subscribed"
    subscriber = Subscriber(
        name=form.get('name'),
        email_address=form.get('email')
    )
    session.add(subscriber)
    session.commit()
    return ''

def getAuthorsForArticle(article_id):
    authors = session.query(Author).join(ArticleAuthor).filter_by(article_id=article_id).all()
    return authors


def getArticlesForAuthor(author_id):
    articles = session.query(Article).join(ArticleAuthor).filter_by(author_id=author_id).all()
    return articles


def getResourcesForArticle(article_id):
    resources = session.query(ArticleResource).filter_by(article_id=article_id).all()
    return resources


def getTitleImageForArticle(article_id):
    try:
        image = session.query(ArticleResource).filter_by(
            article_id=article_id, is_title_img=True
        ).one()
        return image
    except:
        return None
    
    
def getNontitleImagesForArticle(article_id):
    try:
        images = session.query(ArticleResource).filter_by(
            article_id=article_id, is_title_img=False
        ).all()
        return images
    except:
        return None
    

def parseTextElements(article_text, image_list):
    # article_text = re.split(r'\{\{(img|break|foot)?(: ([0-9]+|[a-zA-Z]+)\}\}')
    article_text = re.sub(
        r'\{\{break\}\}', '',
        article_text
    )
    # '<img class="page-break", alt="Page break", src="/static/page-break.png">',
    return article_text


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
    # TODO turn off debug
    app.secret_key = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.secret_key = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()
