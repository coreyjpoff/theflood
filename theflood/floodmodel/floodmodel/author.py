#!/usr/bin/env python2.7

from floodmodel.sqlquery import SQL

class Author:
    def __init__(self, author):
        self.id = author[0]
        self.name = author[1]
        self.bio = author[2]

    # XCJP untested
    @classmethod
    def fromID(authorClass, id):
        author = authorClass.__getAuthorByIDFromDB__(id)
        return authorClass(author)

    # XCJP untested
    @classmethod
    def __getAuthorByIDFromDB__(authorclass, id):
        GET_AUTHOR_BY_ID_QUERY = """
            SELECT * FROM author a
            WHERE a.id = %s; """ % str(id)
        return SQL.queryOneRow(GET_AUTHOR_BY_ID_QUERY)

    @classmethod
    def getAuthorsByArticleID(authorClass, articleID):
        authors = []
        for author in authorClass.__getAuthorsForArticleIDFromDB__(articleID):
            authors.append(authorClass(author))
        return authors

    @classmethod
    def __getAuthorsForArticleIDFromDB__(authorClass, articleID):
        GET_AUTHORS_FOR_ARTICLE_ID_QUERY = """
            SELECT a.id, a.name, a.bio FROM author a
            JOIN article_author aa
            ON a.id = aa.author_id
            WHERE aa.article_id = %s; """ % str(articleID)
        return SQL.queryAllRows(GET_AUTHORS_FOR_ARTICLE_ID_QUERY)
