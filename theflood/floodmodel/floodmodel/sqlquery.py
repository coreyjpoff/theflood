#!/usr/bin/env python2.7

import psycopg2

class SQL:
    @classmethod
    def insert(sqlClass, sqlQuery, params):
        conn = None
        try:
            conn = psycopg2.connect(database="flood", user="flood", password="flood")
            cur = conn.cursor()
            cur.execute(sqlQuery, params)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    @classmethod
    def queryOneRow(sqlClass, sqlQuery, params=None):
        conn = None
        results = None
        try:
            conn = psycopg2.connect(database="flood", user="flood", password="flood")
            cur = conn.cursor()
            sqlClass.__runQuery__(cur, sqlQuery, params)
            results = cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            return results

    @classmethod
    def queryAllRows(sqlClass, sqlQuery, params=None):
        conn = None
        results = None
        try:
            conn = psycopg2.connect(database="flood", user="flood", password="flood")
            cur = conn.cursor()
            sqlClass.__runQuery__(cur, sqlQuery, params)
            results = cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            return results

    @classmethod
    def __runQuery__(sqlClass, cur, sqlQuery, params=None):
        if params is not None:
            cur.execute(sqlQuery, params)
        else:
            cur.execute(sqlQuery)
