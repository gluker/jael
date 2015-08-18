from wtforms import Form, StringField, DateTimeField, TextAreaField, FieldList, FormField, SelectMultipleField, IntegerField, SelectField
from wtforms.validators import ValidationError, Required
from HTMLParser import HTMLParser
from flask import session
from wtforms.csrf.session import SessionCSRF
from . import app

class BForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['SECRET_KEY']

        @property
        def csrf_context(self):
            return session

class RequirementForm(Form):
    condition = StringField('Condition',[Required()])
    comment = StringField('Message')

class ProblemForm(BForm):
    text = TextAreaField('Text',[Required()])
    requirements = FieldList(FormField(RequirementForm))

class CourseForm(BForm):
    name = StringField('Name', [Required()])

class UserForm(BForm):
    id = IntegerField('Id')
    email = StringField('Email')
    type = SelectField('User Type', choices=[('admin','Administrator'),('editor','Editor'),('student','Student')])
    courses = SelectMultipleField('Courses')

class ProblemSetForm(BForm):
    title = StringField('Title', [Required()])
    opens = DateTimeField('Opens', format="%d/%m/%y")
    due = DateTimeField('Due', format="%d/%m/%y")
