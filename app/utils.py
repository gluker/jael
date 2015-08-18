import bbcode
import re
import ast
import random
import string
from models import User
from database import db_session
from . import app

def check_permissions(course_id,user_id):
    user = db_session.query(User).get(user_id)
    if user.type == "admin":
        return "edit"
    elif user.type == "editor":
        #TODO: rights for specific course
        return "edit"
    elif user.type == "student":
        return "view"

def state_gen():
    return ''.join(random.choice(string.ascii_uppercase+string.digits) for i in range(32))

def create_user(session):
    assert db_session.query(User).filter_by(email=session['email']).first() == None
    user = User()
    user.email = session['email']
    if user.email == app.config['ADMIN_EMAIL']:
        user.type="admin"
    else:
        user.type = "student"
    db_session.add(user)
    db_session.commit()
    user = db_session.query(User).filter_by(email=session['email']).one()
    return user.id

def get_user_info(user_id):
    user = db_session.query(User).get(user_id)
    return user

def get_user_id(email):
    user = db_session.query(User).filter_by(email=email).one()
    return user.id

class TreeChecker(ast.NodeVisitor):
    funclist_user = ['sin','cos','abs','ln','tan','ctg']
    funclist_question = ['limit']
    allowed = [
        'Module','Expr','Expression',
        'BoolOp','BinOp','Num','Str', 'Compare','Name',
        'Load',
        'And','Or',
        'Add','Sub','Mult','Div','Mod','Pow',
        'Eq','NotEq','Lt','LtE','Gt','GtE'
        ]

    def generic_visit(self, node):
        if type(node).__name__ == 'Call':
           if node.func.id not in self.funclist_user+self.funclist_question:
               raise ValueError("Function {f} is not allowed".format(f=node.func.id))
        elif type(node).__name__ not in self.allowed:
           raise ValueError("Operation type {tp} is not supported".format(tp=type(node).__name__))


def check_input(input):
    
    tc = TreeChecker()
    try:
        atree = ast.parse(input,'','eval')
        for node in ast.walk(atree):
            tc.generic_visit(node)
    except SyntaxError as e:
        raise e


def bb_to_html(bbtext):
    parser = bbcode.Parser()
    parser.newline = '<br>'
    def input_formatter(tag_name, value, options, parent, context):
        tag ='<input type="'+options['type']
        if 'name' in options:
            tag+='" name="'+options['name']
        if 'value' in options:
            tag+='" value="'+options['value']
        tag+='">'
        return tag
    
    parser.add_formatter('input',input_formatter,standalone = True)
    return parser.format(bbtext)
