#!/usr/bin/env python2.7

from floodmodel.sqlquery import SQL

class Resource:
    def __init__(self, resource):
        self.id = resource[0]
        self.name = resource[1]
        self.articleID = resource[2]
        self.resourceType = resource[3]
        self.isTitleImg = resource[4]
        self.caption = resource[5]
        self.resourceLocation = resource[6]
        self.isAboveText = resource[7]

    # XCJP untested
    @classmethod
    def fromID(resourceClass, id):
        resource = resourceClass.__getResourceByIDFromDB__(id)
        if resource is not None:
            resource = resourceClass(resource)
        return resource

    # XCJP untested
    @classmethod
    def __getResourceByIDFromDB__(resourceClass, id):
        GET_RESOURCE_BY_ID_QUERY = """SELECT * FROM article_resource ar
            WHERE ar.id = %s; """ % str(id)
        return SQL.queryOneRow(GET_RESOURCE_BY_ID_QUERY)

    @classmethod
    def getTitleImageByArticleID(resourceClass, articleID):
        image = resourceClass.__getTitleImageForArticleIDFromDB__(articleID)
        if image is not None:
            image = resourceClass(image)
        return image

    @classmethod
    def __getTitleImageForArticleIDFromDB__(resourceClass, articleID):
        GET_TITLE_IMAGE_FOR_ARTICLE_ID_QUERY = """SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.is_title_img = 't'; """ % str(articleID)
        return SQL.queryOneRow(GET_TITLE_IMAGE_FOR_ARTICLE_ID_QUERY)

    @classmethod
    def getNontitleImagesByArticleID(resourceClass, articleID):
        images = []
        imagesQueryResult = resourceClass.__getNontitleImagesForArticleIDFromDB__(articleID)
        if imagesQueryResult is not None:
            for image in imagesQueryResult:
                images.append(resourceClass(image))
        return images

    @classmethod
    def __getNontitleImagesForArticleIDFromDB__(resourceClass, articleID):
        GET_NONTITLE_IMAGES_FOR_ARTICLE_ID_QUERY = """SELECT * FROM article_resource ar
            WHERE ar.article_id = %s
            AND ar.resource_type != 'audio'
            AND ar.is_title_img = 'f'; """ % str(articleID)
        return SQL.queryAllRows(GET_NONTITLE_IMAGES_FOR_ARTICLE_ID_QUERY)

    @classmethod
    def getAudioByArticleID(resourceClass, articleID):
        audio = resourceClass.__getAudioForArticleIDFromDB__(articleID)
        if audio is not None:
            audio = resourceClass(audio)
        return audio

    @classmethod
    def __getAudioForArticleIDFromDB__(resourceClass, articleID):
        GET_AUDIO_FOR_ARTICLE_ID_QUERY = """SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.resource_type = 'audio'; """ % str(articleID)
        return SQL.queryOneRow(GET_AUDIO_FOR_ARTICLE_ID_QUERY)
