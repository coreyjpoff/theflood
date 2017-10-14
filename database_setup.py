from datetime import date
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()
today = date.today()


# Table definitions
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    signin_email = Column(String(255), nullable=False)
    active_email = Column(String(255))
    role = Column(String(255), nullable=False)
    on_mailer = Column(Boolean, default=False)


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String(1024), nullable=False)
    subtitle = Column(String(1024))
    publish_date = Column(Date, nullable=False, default=today)
    url_desc = Column(String(255), nullable=False)
    html_text = Column(String, nullable=False)
    on_home = Column(Boolean, default=False, index=True)
    featured = Column(Boolean, default=False)
    priority = Column(Integer)
    lead = Column(String)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'publishDate': self.publishDate,
            'url_desc': self.url_desc,
        }


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    bio = Column(String)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio
        }


class ArticleAuthor(Base):
    __tablename__ = 'article_authors'

    article_id = Column(Integer, ForeignKey('article.id'), primary_key=True)
    article = relationship(Article)
    author_id = Column(Integer, ForeignKey('author.id'), primary_key=True)
    author = relationship(Author)


class ArticleResource(Base):
    __tablename__ = 'article_resources'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    article_id = Column(Integer, ForeignKey('article.id'))
    article = relationship(Article)
    resource_type = Column(String(255), nullable=False)
    is_title_img = Column(Boolean, default=False)
    caption = Column(String(1024))
    resource_location = Column(String(255), nullable=False)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'article_id': self.article_id,
            'resource_type': self.resource_type,
            'caption': self.caption,
        }


class Subscriber(Base):
    __tablename__ = 'subscriber'
    
    email_address = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    subscribed = Column(Boolean, default=True)


engine = create_engine('sqlite:///flood.db')
Base.metadata.create_all(engine)
