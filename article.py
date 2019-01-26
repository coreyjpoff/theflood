from datetime import date
from sqlquery import SQL

class Article:
    def __init__(self, id, title, subtitle=None, publish_date=date.today(),
        issue=None, url_desc=None, html_text=None, on_home=False,
        featured=False, priority=None, lead=None, is_hidden=False):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.publish_date = publish_date
        self.issue = issue
        self.url_desc = url_desc
        self.html_text = html_text
        self.on_home = on_home
        self.featured = featured
        self.priority = priority
        self.lead = lead
        self.is_hidden = is_hidden

    @classmethod
    def from_id(articleClass, id):
        article = articleClass.getArticleByIdFromDB(id)
        return articleClass(id, article[1], article[2], article[3], article[4],
            article[5], article[6], article[7], article[8], article[9],
            article[10], article[11])

    @classmethod
    def getArticleByIdFromDB(articleClass, id):
        GET_ARTICLE_BY_ID_QUERY = """
            SELECT * FROM article a
            WHERE a.id = %s; """ % str(id)
        return SQL.queryOneRow(GET_ARTICLE_BY_ID_QUERY)

    def getTitleImageForArticle(self):
        GET_TITLE_IMAGE_BY_ID_QUERY = """
            SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 't'; """ % str(self.id)
        return SQL.queryOneRow(GET_TITLE_IMAGE_BY_ID_QUERY)

    def getNontitleImagesForArticle(self):
        GET_NON_TITLE_IMAGES_BY_ID_QUERY = """
            SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 'f'; """ % str(self.id)
        return SQL.queryAllRows(GET_NON_TITLE_IMAGES_BY_ID_QUERY)

    def getAuthorsForArticle(self):
        GET_AUTHORS_BY_ARTICLE_ID_QUERY = """
            SELECT a.id, a.name, a.bio FROM author a
            JOIN article_author aa
            ON a.id = aa.author_id
            WHERE aa.article_id = %s; """ % str(self.id)
        return SQL.queryAllRows(GET_AUTHORS_BY_ARTICLE_ID_QUERY)
