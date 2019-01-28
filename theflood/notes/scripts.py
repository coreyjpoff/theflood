#!/usr/bin/env python2.7

from sqlquery import SQL

def updateIsAboveTextCol():
    SQL_STATEMENT = """UPDATE article_resource
    SET (is_above_text) = ('f')
    WHERE article_id = 24
    AND is_title_img = 'f';"""
    SQL.insert(SQL_STATEMENT, [])

updateIsAboveTextCol()
