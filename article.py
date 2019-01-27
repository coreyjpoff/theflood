from datetime import date
from sqlquery import SQL
from author import Author
# from resource import Resource

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
        # self.setTitleImageForArticle()
        # self.setNontitleImagesForArticle()

    @classmethod
    def fromID(articleClass, id):
        article = articleClass.__getArticleByIDFromDB__(id)
        return articleClass(id, article[1], article[2], article[3], article[4],
            article[5], article[6], article[7], article[8], article[9],
            article[10], article[11])

    @classmethod
    def __getArticleByIDFromDB__(articleClass, id):
        GET_ARTICLE_BY_ID_QUERY = """
            SELECT * FROM article a
            WHERE a.id = %s; """ % str(id)
        return SQL.queryOneRow(GET_ARTICLE_BY_ID_QUERY)

    def setTitleImageForArticle(self):
        GET_TITLE_IMAGE_BY_ID_QUERY = """
            SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 't'; """ % str(self.id)
        return SQL.queryOneRow(GET_TITLE_IMAGE_BY_ID_QUERY)

    def setNontitleImagesForArticle(self):
        GET_NON_TITLE_IMAGES_BY_ID_QUERY = """
            SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 'f'; """ % str(self.id)
        return SQL.queryAllRows(GET_NON_TITLE_IMAGES_BY_ID_QUERY)

    def setAuthorsForArticle(self):
        self.authors = Author.getAuthorsByArticleID(self.id)

    def setTitleImageForArticle(self):
        self.titleImage = Resource.getTitleImageByArticleID(self.id)

    def setNontitleImagesForArticle(self):
        self.nontitleImages = Resource.getNontitleImagesByArticleID(self.id)
