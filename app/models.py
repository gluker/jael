from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text, Table
from database import Base
from flask_login import UserMixin

courses_table = Table('association', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('course_id', Integer, ForeignKey('course.id'))
)

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
    trials = Column(Integer)
    problemset_id = Column(Integer, ForeignKey("problemset.id"))
    requirements = relationship("Requirement",backref="problem")

class Requirement(Base):
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)
    condition = Column(String(250), nullable=False)
    comment = Column(String(250))
    problem_id = Column(Integer, ForeignKey("problem.id"))

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    courses = relationship("Course", secondary=courses_table)
    problems = relationship("UserProblem")

class UserProblem(Base):
    __tablename__ = 'userproblem'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    problem_id = Column(Integer, ForeignKey("problem.id"))
    rate = Column(Integer)
    problem = relationship("Problem")

