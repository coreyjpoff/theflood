#!/usr/bin/env python2.7

import psycopg2

def create_tables():
    """create tables in database"""
    commands = (
    """
    CREATE TABLE admin_user (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        signin_email VARCHAR(255) NOT NULL,
        active_email VARCHAR(255),
        role VARCHAR(255) NOT NULL,
        on_mailer BOOLEAN DEFAULT 't'
    )
    """,
    """
    CREATE TABLE article (
        id SERIAL PRIMARY KEY,
        title VARCHAR(1024) NOT NULL,
        subtitle VARCHAR(1024),
        publish_date DATE NOT NULL DEFAULT CURRENT_DATE,
        issue INTEGER NOT NULL,
        url_desc VARCHAR(255) NOT NULL,
        html_text VARCHAR NOT NULL,
        on_home BOOLEAN DEFAULT 'f' NOT NULL,
        featured BOOLEAN DEFAULT 'f',
        priority INTEGER DEFAULT 0,
        lead VARCHAR,
        is_hidden BOOLEAN DEFAULT 'f' NOT NULL
    )
    """,
    """
    CREATE TABLE author (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        bio VARCHAR
    )
    """,
    """
    CREATE TABLE article_author (
        article_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        PRIMARY KEY (article_id, author_id),
        FOREIGN KEY (article_id)
            REFERENCES article (id),
        FOREIGN KEY (author_id)
            REFERENCES author (id)
    )
    """,
    """
    CREATE TABLE article_resource (
        id SERIAL PRIMARY KEY NOT NULL,
        name VARCHAR(255) NOT NULL,
        article_id INTEGER REFERENCES article (id),
        resource_type VARCHAR(255) NOT NULL,
        is_title_img BOOLEAN DEFAULT 'f',
        caption VARCHAR(1024),
        resource_location VARCHAR(255) NOT NULL,
        is_above_text BOOLEAN DEFAULT 't'
    )
    """,
    """
    CREATE TABLE subscriber (
        email_address VARCHAR(255) PRIMARY KEY NOT NULL,
        name VARCHAR(255) NOT NULL,
        subscribed BOOLEAN DEFAULT 't'
    )
    """
    )

    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        for command in commands:
            print("Executing command: " + command)
            cur.execute(command)
            conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def drop_tables():
    """drop tables in database"""
    commands = (
    """
    DROP TABLE admin_user CASCADE
    """,
    """
    DROP TABLE article CASCADE
    """,
    """
    DROP TABLE author CASCADE
    """,
    """
    DROP TABLE article_author CASCADE
    """,
    """
    DROP TABLE article_resource CASCADE
    """,
    """
    DROP TABLE subscriber CASCADE
    """
    )

    conn = None
    try:
        conn = psycopg2.connect(database="flood", user="flood", password="flood")
        cur = conn.cursor()
        for command in commands:
            print("Executing command: " + command)
            cur.execute(command)
            conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    drop_tables()
    create_tables()
