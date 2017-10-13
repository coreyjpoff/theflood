from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Article, Author, ArticleAuthor, ArticleResource
from datetime import date
engine = create_engine('sqlite:///flood.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# res3 = ArticleResource(
#   name="ifnotnowpic",
#   article_id="3",
#   caption="Photo by Gili Getz",
#   resource_type="JPG",
#   resource_location="/static/articles/3/ifnotnowpic.jpg",
#   is_title_img=True
# )
#
# auth3 = Author(
#     name="Jacob Friedman",
#     bio="Jacob Friedman is a history teacher and an organizer in the Jewish Resistance. He lives in Highland Park, NJ, works in Newark and organizes in New York City."
# )

artauth3 = ArticleAuthor(
    article_id=3,
    author_id=3
)

res4 = ArticleResource(
  name="StAgnesAnonymous",
  article_id="4",
  caption="St. Agnes and Female Saint by Anonymous (From The Met Archives)",
  resource_type="JPG",
  resource_location="/static/articles/4/StAgnesAnonymous.jpg",
  is_title_img=True
)

auth4 = Author(
    name="Jeannine M. Pitas",
    bio="Jeannine M. Pitas is a writer, teacher, and Spanish-English literary translator currently living in Iowa, where she teaches at the University of Dubuque."
)

artauth4 = ArticleAuthor(
    article_id=4,
    author_id=4
)

res5 = ArticleResource(
  name="Felix",
  article_id="5",
  caption="Photo by Janice Sevre-Duszynska",
  resource_type="JPG",
  resource_location="/static/articles/5/Felix.jpg",
  is_title_img=True
)

auth5 = Author(
    name="Joe Parziale",
    bio="Joe Parziale is a Cofounding Editor at The Flood."
)

artauth5 = ArticleAuthor(
    article_id=5,
    author_id=5
)

res6 = ArticleResource(
  name="Jerusalem",
  article_id="6",
  caption="",
  resource_type="JPG",
  resource_location="/static/articles/6/Jerusalem.jpg",
  is_title_img=True
)

auth6 = Author(
    name="Jonathan Murden",
    bio="Jonathan Murden is an Orthodox Christian and theology undergraduate, currently based in Prague. He is also a columnist for the Full Stop Magazine blog."
)

artauth6 = ArticleAuthor(
    article_id=6,
    author_id=6
)

res7 = ArticleResource(
  name="Fordham",
  article_id="7",
  caption="Photo by Reyna Wang",
  resource_type="JPG",
  resource_location="/static/articles/7/Fordham.jpg",
  is_title_img=True
)

auth7 = Author(
    name="Megan Townsend",
    bio="Megan Townsend is a Cofounding Editor at The Flood."
)

artauth7 = ArticleAuthor(
    article_id=7,
    author_id=7
)

res8 = ArticleResource(
  name="Sharks",
  article_id="8",
  caption="",
  resource_type="JPG",
  resource_location="/static/articles/8/Sharks.jpg",
  is_title_img=True
)

# auth8 is same as auth7

artauth8 = ArticleAuthor(
    article_id=8,
    author_id=7
)

res9 = ArticleResource(
  name="General Sherman and Lakota Dakota leaders discuss Ft Laramie Treaty",
  article_id="9",
  caption="Photo from the National Archives | General Sherman and representatives of the Lakota and Dakota tribes meet at Fort Laramie, Wyoming to sign the treaty of 1868",
  resource_type="JPG",
  resource_location="/static/articles/9/General Sherman and Lakota Dakota leaders discuss Ft Laramie Treaty.jpg",
  is_title_img=True
)

auth9 = Author(
    name="Nathan Albright",
    bio="Nathan Albright is a Cofounding Editor at The Flood."
)

artauth9 = ArticleAuthor(
    article_id=9,
    author_id=9
)

res10 = ArticleResource(
  name="Elizabeth_Culbertson_RailroadStandoff",
  article_id="10",
  caption="Photo by Elizabeth Culbertson",
  resource_type="JPG",
  resource_location="/static/articles/10/Elizabeth_Culbertson_RailroadStandoff.jpg",
  is_title_img=True
)

# auth10 is the same as auth9

artauth10 = ArticleAuthor(
    article_id=10,
    author_id=9
)

res11 = ArticleResource(
  name="Amerigo_Vespucci_names_America",
  article_id="11",
  caption="Discovery of America by Jan van der Straet (from the Metropolitan Museum of Art) | Amerigo Vespucci wakes a Native American woman and names her America",
  resource_type="JPG",
  resource_location="/static/articles/10/Amerigo_Vespucci_names_America.jpeg",
  is_title_img=True
)

# auth11 is the same as auth9

artauth11 = ArticleAuthor(
    article_id=11,
    author_id=9
)

for i in range(3,11):
    if i != 3:
        name = 'res'+str(i)
        session.add(globals()[name])
        session.commit()
    if i != 11 and i !=10 and i != 8 and i != 3:
        name = 'auth'+str(i)
        session.add(globals()[name])
        session.commit()
    name = 'artauth'+str(i)
    session.add(globals()[name])
    session.commit()
