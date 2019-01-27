#!/usr/bin/env python2.7

from datetime import date
from sqlquery import SQL
from author import Author
from resource import Resource

class Article:
    def __init__(self, id, title, subtitle=None, publishDate=date.today(),
        issue=None, urlDesc=None, htmlText=None, onHome=False,
        featured=False, priority=None, lead=None, isHidden=False):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.publishDate = publishDate
        self.issue = issue
        self.urlDesc = urlDesc
        self.htmlText = htmlText
        self.onHome = onHome
        self.featured = featured
        self.priority = priority
        self.lead = lead
        self.isHidden = isHidden
        self.setAuthorsForArticle()
        self.setTitleImageForArticle()
        self.setNontitleImagesForArticle()

    def setAuthorsForArticle(self):
        self.authors = Author.getAuthorsByArticleID(self.id)

    def setTitleImageForArticle(self):
        self.titleImage = Resource.getTitleImageByArticleID(self.id)

    def setNontitleImagesForArticle(self):
        self.nontitleImages = Resource.getNontitleImagesByArticleID(self.id)

    @classmethod
    def fromID(articleClass, id):
        article = articleClass.__getArticleByIDFromDB__(id)
        return articleClass(id, article[1], article[2], article[3], article[4],
            article[5], article[6], article[7], article[8], article[9],
            article[10], article[11])

    @classmethod
    def __getArticleByIDFromDB__(articleClass, id):
        GET_ARTICLE_BY_ID_QUERY = """SELECT * FROM article a
            WHERE a.id = %s; """ % str(id)
        return SQL.queryOneRow(GET_ARTICLE_BY_ID_QUERY)

    @classmethod
    def getHomePageArticles(articleClass):
        articles = []
        articleQueryResults = articleClass.__getAllArticlesMarkedOnHomeNotHidden__()
        for article in articleQueryResults:
            articles.append(articleClass(article[0], article[1], article[2], article[3], article[4],
                article[5], article[6], article[7], article[8], article[9],
                article[10], article[11]))
        return articles

    @classmethod
    def __getAllArticlesMarkedOnHomeNotHidden__(articleClass):
        GET_ALL_ARTICLES_ON_HOME_NOT_HIDDEN = """SELECT * FROM article
            WHERE on_home = 't' AND is_hidden = 'f'
            ORDER BY priority DESC, id ASC; """
        return SQL.queryAllRows(GET_ALL_ARTICLES_ON_HOME_NOT_HIDDEN)

    @classmethod
    def getArchiveArticles(articleClass):
        articles = []
        articleQueryResults = articleClass.__getAllArticlesMarkedNotHidden__()
        for article in articleQueryResults:
            articles.append(articleClass(article[0], article[1], article[2], article[3], article[4],
                article[5], article[6], article[7], article[8], article[9],
                article[10], article[11]))
        return articles

    @classmethod
    def __getAllArticlesMarkedNotHidden__(articleClass):
        GET_ALL_ARTICLES_NOT_HIDDEN = """SELECT * FROM article
            WHERE is_hidden = 'f'
            ORDER BY priority DESC, id ASC; """
        return SQL.queryAllRows(GET_ALL_ARTICLES_NOT_HIDDEN)
