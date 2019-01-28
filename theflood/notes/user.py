#!/usr/bin/env python2.7

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
