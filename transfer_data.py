#!/usr/bin/env python3

import sys

# For the old DB
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker
from database_setup_old import Base, User, Article, Author, ArticleAuthor, \
    ArticleResource, Subscriber

reload(sys)
sys.setdefaultencoding("utf-8")

engine = create_engine('sqlite:///flood.db')
Base.metadata.bind = engine
BDSession = sessionmaker(bind=engine)
session = BDSession()

# For the new DB
import psycopg2


def transfer_authors():
    authors = session.query(Author).order_by(Author.id).all()
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        for author in authors:
            command = """INSERT INTO author (name,bio) VALUES (%s, %s); """
            data = (author.name, author.bio)
            print("Executing command: " + command % data)
            cur.execute(command, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def transfer_articles():
    articles = session.query(Article).order_by(Article.id).all()
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        for article in articles:
            pri = 0
            command = """INSERT INTO article (title,subtitle,publish_date,issue,url_desc,html_text,on_home,featured,priority,lead) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """
            # print ("Article: " + article.title + ", and pri: " + article.priority)
            if article.priority is not None:
                pri = article.priority
            data = (article.title, article.subtitle, article.publish_date, 1, article.url_desc, article.html_text, article.on_home, article.featured, pri, article.lead)
            print("Executing command: " + command % data)
            cur.execute(command, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def transfer_article_authors():
    article_authors = session.query(ArticleAuthor).all()
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        for art_auth in article_authors:
            command = """INSERT INTO article_author (article_id,author_id) VALUES (%s, %s); """
            data = (art_auth.article_id, art_auth.author_id)
            print("Executing command: " + command % data)
            cur.execute(command, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def transfer_article_resources():
    article_resources = session.query(ArticleResource).order_by(ArticleResource.id).all()
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        for resource in article_resources:
            command = """INSERT INTO article_resource (name,article_id,resource_type,is_title_img,caption,resource_location) VALUES (%s, %s, %s, %s, %s, %s); """
            data = (resource.name, resource.article_id, resource.resource_type, resource.is_title_img, resource.caption, resource.resource_location)
            print("Executing command: " + command % data)
            cur.execute(command, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def transfer_subscribers():
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        command = """INSERT INTO subscriber (email_address,name) VALUES (%s,%s); """
        data = [
            ("coreypoff@gmail.com", "Corey Poff"),
            ("albrightkatrina@gmail.com", "Katrina Albright"),
            ("joseph.parziale@gmail.com", "Joe Parziale"),
            ("tylerkenthill1992@gmail.com", "Tyler Hill"),
            ("thefloodmag@gmail.com", "Thefloodmag"),
            ("hhauge@fordham.edu", "Haley Hauge"),
            ("vickielmaloney@gmail.com", "Vickie Maloney"),
            ("lgmez36@gmail.com", "Luis A Gomez"),
            ("hillfletche@fordham.edu", "Jeannine Hill Fletcher"),
            ("rmasvg@gmail.com", "Richard Allen"),
            ("jennerg@gmail.com", "Jenn Gahres"),
            ("loughransiobhan@gmail.com", "Siobhan Loughran"),
            ("aloughli@nd.edu", "Abigail Loughlin"),
            ("esommers13@gmail.com", "Eric Sommers"),
            ("jchoman@owu.edu", "John Homan"),
            ("tpgates@bigpond.com", "Patricia"),
            ("opgal67@aol.com", "Sr, Nancy Richter, OP"),
            ("lauriegee@gmail.com", "Lauria Galbraith"),
            ("neil.m.ashton@gmail.com", "Neil Ashton"),
            ("voidisyinyang@gmail.com", "drew hempel"),
            ("aryan35@fordham.edu", "Ally Ryan"),
            ("Tlo99@fastmail.net", "T. Owens"),
            ("davidcbloomfield@gmail.com", "David Bloomfield"),
            ("cygaleota@gmail.com", "cynthia galeota"),
            ("Jessicamary109@gmail.com", "Jessica"),
            ("bkozee@jesuitvolunteers.org", "Barb Kozee"),
            ("Maren.grossman@gmail.com", "Maren Grossman"),
            ("airwinai@gmail.com", "Andrew Irwin"),
            ("bkhey2@gmail.com", "Brian Hey"),
            ("willcurt@iu.edu", "Curtis Williamson"),
            ("mkglenn01@gmail.com", "MaryKate Glenn"),
        ]
        for sub in data:
            print("Executing command: " + command % sub)
            cur.execute(command, sub)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def verify_articles():
    oldArticles = session.query(Article).order_by(Article.id).all()
    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        cur.execute("""SELECT * FROM article ORDER BY id; """)
        newArticles = cur.fetchall()
        for article in oldArticles:
            newArticle = newArticles[article.id-1]
            print("OLD | NEW")
            print(str(article.id) + "|" + str(newArticle[0]))
            print(article.title + "|" + newArticle[1])
            print(str(article.subtitle) + "|" + str(newArticle[2]))
            print(str(article.publish_date) + "|" + str(newArticle[3]))
            print("No old art issue" + "|" + str(newArticle[4]))
            print(article.url_desc + "|" + newArticle[5])
            # print(article.html_text + "|" + newArticle[6])
            print(str(article.on_home) + "|" + str(newArticle[7]))
            print(str(article.featured) + "|" + str(newArticle[8]))
            print(str(article.priority) + "|" + str(newArticle[9]))
            print(str(article.lead) + "|" + str(newArticle[10]))
            print("----------------------")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    transfer_authors()
    transfer_articles()
    transfer_article_authors()
    transfer_article_resources()
    # verify_articles()
    transfer_subscribers()
