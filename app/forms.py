from wtforms import Form, StringField, DateTimeField, TextAreaField, FieldList, FormField
from wtforms.validators import ValidationError, Required
from HTMLParser import HTMLParser

class TextParser(HTMLParser):
    allowed_tags = ['input','br','label','div','span','h1','h2']
    def handle_starttag(self,tag,attrs):
        if tag not in allowed_tags:
            raise ("Unallowed tag %s found", tag)

def valid_html():
    message = "Invalid html" 
    def _valid_html(form,field):
        try:
            tparser = TextParser()
            tparser.feed(field.data)
        except:
            raise ValidationError(message)

    return _valid_html

class RequirementForm(Form):
    condition = StringField('Condition',[Required()])
    message = StringField('Message')

class ProblemForm(Form):
    text = TextAreaField('Text',[Required(),valid_html()])
    requirements = FieldList(FormField(RequirementForm))


class ProblemSetForm(Form):
    title = StringField('Title')
    opens = DateTimeField('Opens', format="%d/%m/%y")
    due = DateTimeField('Due', format="%d/%m/%y")
