from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Article, Author, ArticleAuthor, ArticleResource
from datetime import date
engine = create_engine('sqlite:///flood.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

today = date.today()

TEXT_1 = "By so delight of showing neither believe he present. Deal sigh up in shew away when. Pursuit express no or prepare replied. Wholly formed old latter future but way she. Day her likewise smallest expenses judgment building man carriage gay. Considered introduced themselves mr to discretion at. Means among saw hopes for. Death mirth in oh learn he equal on. He as compliment unreserved projecting. Between had observe pretend delight for believe. Do newspaper questions consulted sweetness do. Our sportsman his unwilling fulfilled departure law. Now world own total saved above her cause table. Wicket myself her square remark the should far secure sex. Smiling cousins warrant law explain for whether. Throwing consider dwelling bachelor joy her proposal laughter. Raptures returned disposed one entirely her men ham. By to admire vanity county an mutual as roused. Of an thrown am warmly merely result depart supply. Required honoured trifling eat pleasure man relation."
TEXT_2 = "Carried nothing on am warrant towards. Polite in of in oh needed itself silent course. Assistance travelling so especially do prosperous appearance mr no celebrated. Wanted easily in my called formed suffer. Songs hoped sense as taken ye mirth at. Believe fat how six drawing pursuit minutes far. Same do seen head am part it dear open to. Whatever may scarcely judgment had. Manor we shall merit by chief wound no or would. Oh towards between subject passage sending mention or it. Sight happy do burst fruit to woody begin at. Assurance perpetual he in oh determine as. The year paid met him does eyes same. Own marianne improved sociable not out. Thing do sight blush mr an. Celebrated am announcing delightful remarkably we in literature it solicitude. Design use say piqued any gay supply. Front sex match vexed her those great."

newArticle1 = Article(
    title = "The very first test article",
    subtitle = "The first subtitle",
    publish_date = date(today.year, today.month, today.day),
    url_desc = "the-very-first",
    html_text = TEXT_1,
    on_home = True,
    featured = True
)
session.add(newArticle1)
session.commit()

newAuthor1 = Author(name = "Corey Poff")
session.add(newAuthor1)
session.commit()

newAuthor2 = Author(name = "Jonah G.-S.")
session.add(newAuthor2)
session.commit()

newArticleAuthor1 = ArticleAuthor(
    article_id = newArticle1.id,
    author_id = newAuthor1.id
)
session.add(newArticleAuthor1)
session.commit()

newArticleAuthor2 = ArticleAuthor(
    article_id = newArticle1.id,
    author_id = newAuthor2.id
)
session.add(newArticleAuthor2)
session.commit()

newArticleResource1 = ArticleResource(
    name = "The first test resource",
    article_id = newArticle1.id,
    caption = "This is just a test",
    resource_type = 'JPG',
    resource_location = "This is the resource text itsleffff"
)
session.add(newArticleResource1)
session.commit()

newArticle2 = Article(
    title = "Some BS Article That I Didn't Write",
    subtitle = "Eyyy do you wanna have a subtitle?",
    publish_date = date(today.year, today.month-1, today.day+3),
    url_desc = "some-bs-article",
    html_text = TEXT_2,
    on_home = True,
    featured = False
)
session.add(newArticle2)
session.commit()

newArticleAuthor3 = ArticleAuthor(
    article_id = newArticle2,
    author_id = newAuthor1
)
session.add(newArticle2)
session.commit()
