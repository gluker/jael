from wtforms import Form, StringField, DateTimeField, TextAreaField, FieldList, FormField
from wtforms.validators import ValidationError, Required

class RequirementForm(Form):
    condition = StringField('Condition',[Required()])
    message = StringField('Message')

class ProblemForm(Form):
    text = TextAreaField('Text',[Required()])
    requirements = FieldList(FormField(RequirementForm))


class ProblemSetForm(Form):
    title = StringField('Title')
    opens = DateTimeField('Opens', format="%d/%m/%y")
    due = DateTimeField('Due', format="%d/%m/%y")
