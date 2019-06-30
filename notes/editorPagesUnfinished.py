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
@app.route('/edit/new', methods=['GET', 'POST'])
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

@app.route('/edit/authors/')
def editAuthorsHome():
    authors = getAllAuthors()
    return render_template('editAuthors.html', authors=authors)

@app.route('/edit/authors/<int:auth_id>/', methods=['GET', 'POST'])
def editAuthor(auth_id):
    author = getAuthor(auth_id)
    if request.method == 'POST':
        saveExistingAuthorFromForm(author, request.form)
        return redirect(url_for('editAuthorsHome'))
    else:
        return render_template('editAuthor.html', author=author)

@app.route('/edit/authors/new/', methods=['GET', 'POST'])
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

@app.route('/email-list')
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
@app.route('/edit/upload/<int:article_id>/<string:type>', methods=['GET', 'POST'])
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
@app.route('/edit/delete/resource/<int:id>/<int:article_id>')
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
