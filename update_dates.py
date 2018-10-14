#!/usr/bin/env python3

import sys
import psycopg2

def update_dates():
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        sql = """SELECT * FROM article
            WHERE issue = 2; """
        cur.execute(sql)
        articles = cur.fetchall()
        for article in articles:
            print article
            sql = """UPDATE article SET (publish_date)
                =(%s) WHERE id = %s;"""
            data = ('2018-10-13', article[0])
            cur.execute(sql, data)
            conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    update_dates()
