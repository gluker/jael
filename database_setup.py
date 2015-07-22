from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text
from sqlalchemy.ext.declatarive import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class ProblemSet(Base):
    __tablename__ = 'problemset'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    opens = Column(Date)
    due = Column(Date)

class Problem(Base):
    __tablename__ = 'problem'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    
class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    type = Column(String(250))
