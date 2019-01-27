#!/usr/bin/env python2.7

from sqlquery import SQL

class Subscriber:
    def __init__(self, email, name):
        self.email = email
        self.name = name

    @classmethod
    def saveSubscriberFromForm(subscriberClass, form):
        error = subscriberClass.__verifySubscriberForm__(form)
        if error is not None:
            return error
        subscriber = subscriberClass.__initializeSubscriberFromForm__(form)
        subscriberClass.__saveNewSubscriber__((subscriber.email, subscriber.name))
        return None

    @classmethod
    def __verifySubscriberForm__(subscriberClass, form):
        if not form.get('name'):
            return "Name is required"
        if not form.get('email'):
            return "Email is required"
        if subscriberClass.__isSubscriber__(form.get('email')):
            return "That email address is already subscribed"
        return None

    @classmethod
    def __isSubscriber__(subscriberClass, email):
        return subscriberClass.__findSubscriber__(email) != None

    @classmethod
    def __findSubscriber__(subscriberClass, email):
        FIND_SUBSCRIBER_FROM_EMAIL = """SELECT * FROM subscriber s
            WHERE s.email_address = '%s'; """ % email
        subscriber = SQL.queryOneRow(FIND_SUBSCRIBER_FROM_EMAIL)
        return subscriber

    @classmethod
    def __initializeSubscriberFromForm__(subscriberClass, form):
        return subscriberClass(form.get('email'), form.get('name'))

    @classmethod
    def __saveNewSubscriber__(subscriberClass, data):
        CREATE_SUBSCRIBER = """INSERT INTO subscriber (email_address,name)
            VALUES (%s, %s); """
        SQL.insert(CREATE_SUBSCRIBER, data)
