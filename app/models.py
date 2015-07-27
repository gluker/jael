from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text
from database import Base

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    problemsets = relationship("ProblemSet",backref="course")

class ProblemSet(Base):
    __tablename__ = 'problemset'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    opens = Column(Date)
    due = Column(Date)
    course_id = Column(Integer, ForeignKey("course.id"))
    problems = relationship("Problem",backref="problemset")

class Problem(Base):
    __tablename__ = 'problem'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    problemset_id = Column(Integer, ForeignKey("problemset.id"))
    questions = relationship("Question",backref="problem")

class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    type = Column(String(250))
    problem_id = Column(Integer, ForeignKey("problem.id"))
    requirements = relationship("Requirement", backref="question")

class Requirement(Base):
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)
    type = Column(String(250)) #TODO: some sort of enum
    value = Column(Integer)
    question_id = Column(Integer, ForeignKey("question.id"))
