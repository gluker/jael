from wtforms import Form, StringField, DateTimeField


class ProblemSetForm(Form):
   title = StringField('Title')
   opens = DateTimeField('Opens', format="%d/%m/%y")
   due = DateTimeField('Due', format="%d/%m/%y")
