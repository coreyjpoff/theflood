#!/usr/bin/env python2.7

from sqlquery import SQL
from author import Author
from resource import Resource

class Article:
    def __init__(self, article):
        self.id = article[0]
        self.title = article[1]
        self.subtitle = article[2]
        self.publishDate = article[3]
        self.issue = article[4]
        self.urlDesc = article[5]
        self.htmlText = article[6]
        self.onHome = article[7]
        self.featured = article[8]
        self.priority = article[9]
        self.lead = article[10]
        self.isHidden = article[11]
        self.__getAuthorsForArticle__()
        self.__getTitleImageForArticle__()
        self.__getNontitleImagesForArticle__()
        self.__getAudioFile__()

    def __getAuthorsForArticle__(self):
        self.authors = Author.getAuthorsByArticleID(self.id)

    def __getTitleImageForArticle__(self):
        self.titleImage = Resource.getTitleImageByArticleID(self.id)

    def __getNontitleImagesForArticle__(self):
        self.nontitleImages = Resource.getNontitleImagesByArticleID(self.id)

    def __getAudioFile__(self):
        self.audioFile = Resource.getAudioByArticleID(self.id)

    @classmethod
    def fromID(articleClass, id):
        article = articleClass.__getArticleByIDFromDB__(id)
        return articleClass(article)

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
            articles.append(articleClass(article))
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
            articles.append(articleClass(article))
        return articles

    @classmethod
    def __getAllArticlesMarkedNotHidden__(articleClass):
        GET_ALL_ARTICLES_NOT_HIDDEN = """SELECT * FROM article
            WHERE is_hidden = 'f'
            ORDER BY priority DESC, id ASC; """
        return SQL.queryAllRows(GET_ALL_ARTICLES_NOT_HIDDEN)
