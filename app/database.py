from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from . import app

engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db(engine=engine):
    import models
    Base.metadata.create_all(engine)

def drop_db(engine=engine):
    assert app.config['TESTING'] 
    Base.metadata.drop_all(engine)

