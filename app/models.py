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
    requirements = relationship("Requirement",backref="problem")

class Requirement(Base):
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)
    condition = Column(String(250), nullable=False)
    comment = Column(String(250))
    problem_id = Column(Integer, ForeignKey("problem.id"))
