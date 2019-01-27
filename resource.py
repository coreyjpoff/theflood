#!/usr/bin/env python2.7

from sqlquery import SQL

class Resource:
    def __init__(self, id, name, articleID, resourceType=None, isTitleImg=False,
        caption=None, resourceLocation=None):
        self.id = id
        self.name = name
        self.articleID = articleID
        self.resourceType = resourceType
        self.isTitleImg = isTitleImg
        self.caption = caption
        self.resourceLocation = resourceLocation

    # XCJP untested
    @classmethod
    def fromID(resourceClass, id):
        resource = resourceClass.__getResourceByIDFromDB__(id)
        if resource is not None:
            resource = resourceClass(id, resource[1], resource[2], resource[3],
                resource[4], resource[5], resource[6])
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
            image = resourceClass(image[0], image[1], image[2], image[3],
                image[4], image[5], image[6])
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
                images.append(resourceClass(image[0], image[1], image[2],
                    image[3], image[4], image[5], image[6]))
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
            audio = resourceClass(audio[0], audio[1], audio[2], audio[3],
                audio[4], audio[5], audio[6])
        return audio

    @classmethod
    def __getAudioForArticleIDFromDB__(resourceClass, articleID):
        GET_AUDIO_FOR_ARTICLE_ID_QUERY = """SELECT * FROM article_resource a
            WHERE a.article_id = %s
            AND a.resource_type = 'audio'; """ % str(articleID)
        return SQL.queryOneRow(GET_AUDIO_FOR_ARTICLE_ID_QUERY)
